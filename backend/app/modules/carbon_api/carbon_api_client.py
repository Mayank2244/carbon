"""
Carbon API Client
Integrates with Electricity Maps and Climatiq APIs to fetch carbon intensity data.
Features a Smart Static Fallback for robust operation without API keys.
"""

import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from app.core.logging import get_logger
from app.core.config import settings
from app.core.exceptions import CarbonSenseException
from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_data import (
    CarbonData,
    ElectricityMapsResponse,
    ClimatiqResponse
)

logger = get_logger(__name__)


class CarbonAPIException(CarbonSenseException):
    """Exception raised for Carbon API errors."""
    pass


class CarbonAPIClient:
    """
    High-level client for aggregating real-time carbon intensity data.

    Interfaces with Electricity Maps and Climatiq APIs.
    Implements a "Smart Static Fallback" system to provide reasonable estimates
    based on region when live API data is unavailable.

    Attributes:
        cache_manager (CacheManager): Instance used to store retrieved carbon data.
        electricity_maps_api_key (str): Key for primary carbon data provider.
        climatiq_api_key (str): Key for secondary provider.
    """
    
    # API endpoints
    ELECTRICITY_MAPS_BASE_URL = "https://api.electricitymap.org/v3"
    CLIMATIQ_BASE_URL = "https://api.climatiq.io/data/v1"
    
    # Global Fallback Defaults
    FALLBACK_CARBON_INTENSITY = 475.0  # gCO2/kWh (Global Average)
    FALLBACK_RENEWABLE_PERCENTAGE = 29.0
    FALLBACK_FOSSIL_PERCENTAGE = 71.0
    
    # Smart Static Fallback Data (gCO2/kWh)
    # Approximate averages for major regions to use when APIs fail/missing keys
    STATIC_FALLBACK_DATA = {
        # Europe
        "FR": 50.0,   # France (Nuclear)
        "DE": 450.0,  # Germany (Mixed)
        "GB": 230.0,  # UK (Mixed)
        "PL": 750.0,  # Poland (Coal)
        "SE": 30.0,   # Sweden (Hydro/Nuclear)
        "NO": 20.0,   # Norway (Hydro)
        "ES": 190.0,  # Spain (Mixed)
        "IT": 300.0,  # Italy (Gas)
        
        # North America
        "US": 380.0,      # US Average
        "US-CAL-CISO": 200.0, # California (Cleaner)
        "US-TEX-ERCO": 400.0, # Texas (Gas/Wind)
        "US-NY-NYIS": 250.0,  # New York
        "CA": 130.0,      # Canada (Hydro)
        
        # Asia
        "CN": 550.0,  # China (Coal/Renewables)
        "JP": 500.0,  # Japan (Gas/Coal)
        "IN": 700.0,  # India (Coal)
        
        # Oceania
        "AU": 600.0,  # Australia (Coal/Solar)
    }
    
    def __init__(
        self,
        cache_manager: CacheManager,
        electricity_maps_api_key: Optional[str] = None,
        climatiq_api_key: Optional[str] = None
    ):
        """
        Initialize Carbon API Client.
        
        Args:
            cache_manager: Cache manager instance
            electricity_maps_api_key: API key for Electricity Maps
            climatiq_api_key: API key for Climatiq
        """
        self.cache_manager = cache_manager
        self.electricity_maps_api_key = electricity_maps_api_key or settings.electricity_maps_api_key
        self.climatiq_api_key = climatiq_api_key or settings.climatiq_api_key
        
        # Initialize validation
        self._validate_api_keys()
        
        logger.info("CarbonAPIClient initialized (WattTime removed, Smart Fallback enabled)")
    
    def _validate_api_keys(self):
        """Log warnings for missing API keys."""
        if not self.electricity_maps_api_key:
            logger.warning("Electricity Maps API key not configured. Real-time data may be unavailable.")
        if not self.climatiq_api_key:
            logger.warning("Climatiq API key not configured. Using Smart Static Fallback.")
    
    async def get_carbon_intensity(
        self,
        latitude: float,
        longitude: float
    ) -> CarbonData:
        """
        Retrieves carbon intensity for coordinates with fallback chain:
        1. Electricity Maps (Real-time)
        2. Climatiq (Emission Factors)
        3. Smart Static Fallback (Region-based Average)
        4. Global Average Fallback
        """
        # Validate coordinates
        if not (-90 <= latitude <= 90):
            raise ValueError(f"Invalid latitude: {latitude}")
        if not (-180 <= longitude <= 180):
            raise ValueError(f"Invalid longitude: {longitude}")
        
        # Check cache
        cache_key = f"carbon:coords:{latitude:.4f},{longitude:.4f}"
        cached_data = await self.cache_manager.get(cache_key)
        
        if cached_data:
            logger.info(f"Cache hit for coordinates ({latitude}, {longitude})")
            return CarbonData(**cached_data)
        
        logger.info(f"Fetching carbon intensity for coordinates ({latitude}, {longitude})")
        
        # 1. Try Electricity Maps (Primary)
        try:
            carbon_data = await self._fetch_from_electricity_maps(latitude, longitude)
            await self._cache_carbon_data(cache_key, carbon_data)
            return carbon_data
        except Exception as e:
            logger.warning(f"Electricity Maps API failed: {str(e)}")
        
        # 2. Try Climatiq (Secondary)
        try:
            carbon_data = await self._fetch_from_climatiq(latitude, longitude)
            await self._cache_carbon_data(cache_key, carbon_data)
            return carbon_data
        except Exception as e:
            logger.warning(f"Climatiq API failed: {str(e)}")
        
        # 3. Smart Static Fallback
        # Determine region code first
        region_code = self._get_climatiq_region_code(latitude, longitude)
        return self._get_fallback_data(region_code=region_code, latitude=latitude, longitude=longitude)
    
    async def get_region_carbon(self, region_code: str) -> CarbonData:
        """Retrieves carbon intensity for a region code with fallback chain."""
        # Check cache
        cache_key = f"carbon:region:{region_code}"
        cached_data = await self.cache_manager.get(cache_key)
        
        if cached_data:
            logger.info(f"Cache hit for region {region_code}")
            return CarbonData(**cached_data)
        
        logger.info(f"Fetching carbon intensity for region {region_code}")
        
        # 1. Try Electricity Maps
        try:
            carbon_data = await self._fetch_region_from_electricity_maps(region_code)
            await self._cache_carbon_data(cache_key, carbon_data)
            return carbon_data
        except Exception as e:
            logger.warning(f"Electricity Maps API failed for region: {str(e)}")
        
        # 2. Try Climatiq
        try:
            carbon_data = await self._fetch_region_from_climatiq(region_code)
            await self._cache_carbon_data(cache_key, carbon_data)
            return carbon_data
        except Exception as e:
            logger.warning(f"Climatiq API failed for region: {str(e)}")
        
        # 3. Smart Static Fallback
        return self._get_fallback_data(region_code=region_code)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True
    )
    async def _fetch_from_electricity_maps(self, latitude: float, longitude: float) -> CarbonData:
        """Fetch from Electricity Maps by coordinates."""
        if not self.electricity_maps_api_key:
            raise CarbonAPIException("Electricity Maps API key not configured")
        
        url = f"{self.ELECTRICITY_MAPS_BASE_URL}/carbon-intensity/latest"
        headers = {"auth-token": self.electricity_maps_api_key}
        params = {"lat": latitude, "lon": longitude}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return ElectricityMapsResponse(**data).to_carbon_data(latitude=latitude, longitude=longitude)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True
    )
    async def _fetch_region_from_electricity_maps(self, region_code: str) -> CarbonData:
        """Fetch from Electricity Maps by region."""
        if not self.electricity_maps_api_key:
            raise CarbonAPIException("Electricity Maps API key not configured")
        
        url = f"{self.ELECTRICITY_MAPS_BASE_URL}/carbon-intensity/latest"
        headers = {"auth-token": self.electricity_maps_api_key}
        params = {"zone": region_code}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            return ElectricityMapsResponse(**data).to_carbon_data()
    
    def _get_climatiq_region_code(self, latitude: float, longitude: float) -> str:
        """Map coordinates to simplified region code (ISO 3166-1 alpha-2)."""
        # North America
        if 24.0 <= latitude <= 49.0 and -125.0 <= longitude <= -66.0: return "US"
        elif 41.0 <= latitude <= 83.0 and -141.0 <= longitude <= -52.0: return "CA"
        # Europe
        elif 36.0 <= latitude <= 71.0 and -10.0 <= longitude <= 40.0:
            if 41.0 <= latitude <= 51.0 and -5.0 <= longitude <= 10.0: return "FR"
            elif 47.0 <= latitude <= 55.0 and 5.0 <= longitude <= 15.0: return "DE"
            elif 50.0 <= latitude <= 59.0 and -8.0 <= longitude <= 2.0: return "GB"
            elif 51.0 <= latitude <= 55.0 and 14.0 <= longitude <= 24.0: return "PL"
            return "DE" # Default Europe
        # Asia
        elif 20.0 <= latitude <= 45.0 and 122.0 <= longitude <= 154.0: return "JP"
        elif 18.0 <= latitude <= 54.0 and 73.0 <= longitude <= 135.0: return "CN"
        # Oceania
        elif -44.0 <= latitude <= -10.0 and 112.0 <= longitude <= 154.0: return "AU"
        
        return "US" # Default Global
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True
    )
    async def _fetch_from_climatiq(self, latitude: float, longitude: float) -> CarbonData:
        """Fetch from Climatiq API by coordinates."""
        if not self.climatiq_api_key:
            raise CarbonAPIException("Climatiq API key not configured")
        
        region_code = self._get_climatiq_region_code(latitude, longitude)
        return await self._fetch_region_from_climatiq(region_code)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(httpx.HTTPStatusError),
        reraise=True
    )
    async def _fetch_region_from_climatiq(self, region_code: str) -> CarbonData:
        """Fetch from Climatiq API by region."""
        if not self.climatiq_api_key:
            raise CarbonAPIException("Climatiq API key not configured")
        
        url = f"{self.CLIMATIQ_BASE_URL}/estimate"
        headers = {"Authorization": f"Bearer {self.climatiq_api_key}", "Content-Type": "application/json"}
        payload = {
            "emission_factor": {
                "activity_id": "electricity-supply_grid-source_supplier_mix",
                "region": region_code,
                "year": "2023",
                "data_version": "^30"
            },
            "parameters": {"energy": 1, "energy_unit": "kWh"}
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return ClimatiqResponse(**data).to_carbon_data(region_code=region_code)
            
    def _get_fallback_data(
        self,
        region_code: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None
    ) -> CarbonData:
        """
        Smart Static Fallback.
        Returns region-specific static average if available, else global average.
        """
        intensity = self.FALLBACK_CARBON_INTENSITY
        source = "fallback_global_avg"
        
        # Check Smart Static Data
        if region_code and region_code in self.STATIC_FALLBACK_DATA:
            intensity = self.STATIC_FALLBACK_DATA[region_code]
            source = f"fallback_static_{region_code}"
            logger.info(f"Using Smart Static Fallback for {region_code}: {intensity} gCO2/kWh")
        else:
            logger.warning("Using Global Average Fallback")
            
        return CarbonData(
            carbon_intensity=intensity,
            renewable_percentage=self.FALLBACK_RENEWABLE_PERCENTAGE,
            fossil_fuel_percentage=self.FALLBACK_FOSSIL_PERCENTAGE,
            timestamp=datetime.utcnow(),
            data_source=source,
            region_code=region_code,
            latitude=latitude,
            longitude=longitude
        )
    
    async def _cache_carbon_data(self, cache_key: str, carbon_data: CarbonData) -> None:
        """Cache carbon data."""
        await self.cache_manager.set(
            cache_key,
            carbon_data.dict(),
            ttl=settings.carbon_cache_ttl
        )
