"""
Comprehensive tests for Carbon API Client.
Tests API calls, caching, retry logic, and error handling.
"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from app.modules.carbon_api import CarbonAPIClient, CarbonData, CarbonAPIException
from app.modules.carbon_api.carbon_data import ElectricityMapsResponse, WattTimeResponse


class TestCarbonData:
    """Tests for CarbonData model."""
    
    def test_carbon_data_validation(self, sample_carbon_data):
        """Test CarbonData model validation."""
        assert sample_carbon_data.carbon_intensity == 250.5
        assert sample_carbon_data.renewable_percentage == 64.8
        assert sample_carbon_data.fossil_fuel_percentage == 35.2
        assert sample_carbon_data.data_source == "electricity_maps"
    
    def test_carbon_data_invalid_percentage(self):
        """Test that invalid percentages raise validation errors."""
        with pytest.raises(ValueError):
            CarbonData(
                carbon_intensity=250.5,
                renewable_percentage=150.0,  # Invalid: > 100
                fossil_fuel_percentage=35.2,
                timestamp=datetime.utcnow(),
                data_source="test"
            )
    
    def test_carbon_data_invalid_coordinates(self):
        """Test that invalid coordinates raise validation errors."""
        with pytest.raises(ValueError):
            CarbonData(
                carbon_intensity=250.5,
                renewable_percentage=50.0,
                fossil_fuel_percentage=50.0,
                timestamp=datetime.utcnow(),
                data_source="test",
                latitude=95.0  # Invalid: > 90
            )


class TestElectricityMapsResponse:
    """Tests for Electricity Maps response conversion."""
    
    def test_to_carbon_data_conversion(self, mock_electricity_maps_response):
        """Test conversion from Electricity Maps response to CarbonData."""
        em_response = ElectricityMapsResponse(**mock_electricity_maps_response)
        carbon_data = em_response.to_carbon_data(latitude=37.7749, longitude=-122.4194)
        
        assert carbon_data.carbon_intensity == 250.5
        assert carbon_data.renewable_percentage == 64.8
        assert carbon_data.fossil_fuel_percentage == 35.2
        assert carbon_data.data_source == "electricity_maps"
        assert carbon_data.region_code == "US-CA"
        assert carbon_data.latitude == 37.7749
        assert carbon_data.longitude == -122.4194


class TestWattTimeResponse:
    """Tests for WattTime response conversion."""
    
    def test_to_carbon_data_conversion(self, mock_watttime_response):
        """Test conversion from WattTime response to CarbonData."""
        wt_response = WattTimeResponse(**mock_watttime_response)
        carbon_data = wt_response.to_carbon_data(latitude=37.7749, longitude=-122.4194)
        
        # 1200.5 lbs CO2/MWh = (1200.5 * 453.592) / 1000 = 544.54 gCO2/kWh
        assert abs(carbon_data.carbon_intensity - 544.54) < 0.1
        assert carbon_data.data_source == "watttime"
        assert carbon_data.region_code == "CAISO_NORTH"


class TestCarbonAPIClient:
    """Tests for CarbonAPIClient."""
    
    @pytest.mark.asyncio
    async def test_get_carbon_intensity_cache_hit(
        self,
        carbon_api_client,
        mock_cache_manager,
        sample_carbon_data
    ):
        """Test that cached data is returned without API call."""
        # Setup cache to return data
        mock_cache_manager.get.return_value = sample_carbon_data.dict()
        
        result = await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
        
        assert result.carbon_intensity == sample_carbon_data.carbon_intensity
        assert result.data_source == "electricity_maps"
        mock_cache_manager.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_carbon_intensity_cache_miss_success(
        self,
        carbon_api_client,
        mock_cache_manager,
        mock_electricity_maps_response
    ):
        """Test successful API call on cache miss."""
        # Setup cache miss
        mock_cache_manager.get.return_value = None
        
        # Mock httpx response
        mock_response = MagicMock()
        mock_response.json.return_value = mock_electricity_maps_response
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
            
            assert result.carbon_intensity == 250.5
            assert result.data_source == "electricity_maps"
            mock_cache_manager.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_carbon_intensity_fallback_to_watttime(
        self,
        carbon_api_client,
        mock_cache_manager,
        mock_watttime_response,
        mock_watttime_login_response
    ):
        """Test fallback to WattTime when Electricity Maps fails."""
        mock_cache_manager.get.return_value = None
        
        call_count = 0
        
        async def mock_get(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_response = MagicMock()
            
            if call_count == 1:
                # First call: Electricity Maps fails
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "API Error", request=MagicMock(), response=MagicMock()
                )
            elif call_count == 2:
                # Second call: WattTime login
                mock_response.json.return_value = mock_watttime_login_response
                mock_response.raise_for_status = MagicMock()
            else:
                # Third call: WattTime data
                mock_response.json.return_value = mock_watttime_response
                mock_response.raise_for_status = MagicMock()
            
            return mock_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = mock_get
            
            result = await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
            
            assert result.data_source == "watttime"
            assert result.carbon_intensity > 0
    
    @pytest.mark.asyncio
    async def test_get_carbon_intensity_fallback_data(
        self,
        carbon_api_client,
        mock_cache_manager
    ):
        """Test fallback to global average when all APIs fail."""
        mock_cache_manager.get.return_value = None
        
        # Mock all API calls to fail
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "API Error", request=MagicMock(), response=MagicMock()
            )
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
            
            assert result.data_source == "fallback"
            assert result.carbon_intensity == 475.0  # Global average
            assert result.renewable_percentage == 29.0
    
    @pytest.mark.asyncio
    async def test_get_carbon_intensity_invalid_coordinates(self, carbon_api_client):
        """Test that invalid coordinates raise ValueError."""
        with pytest.raises(ValueError, match="Invalid latitude"):
            await carbon_api_client.get_carbon_intensity(95.0, -122.4194)
        
        with pytest.raises(ValueError, match="Invalid longitude"):
            await carbon_api_client.get_carbon_intensity(37.7749, 200.0)
    
    @pytest.mark.asyncio
    async def test_get_region_carbon_success(
        self,
        carbon_api_client,
        mock_cache_manager,
        mock_electricity_maps_response
    ):
        """Test successful region-based query."""
        mock_cache_manager.get.return_value = None
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_electricity_maps_response
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await carbon_api_client.get_region_carbon("US-CA")
            
            assert result.carbon_intensity == 250.5
            assert result.region_code == "US-CA"
            assert result.data_source == "electricity_maps"
    
    @pytest.mark.asyncio
    async def test_cache_ttl_configuration(
        self,
        carbon_api_client,
        mock_cache_manager,
        mock_electricity_maps_response
    ):
        """Test that cache TTL is properly configured."""
        mock_cache_manager.get.return_value = None
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_electricity_maps_response
        mock_response.raise_for_status = MagicMock()
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
            
            # Verify cache.set was called with TTL from settings
            mock_cache_manager.set.assert_called_once()
            call_args = mock_cache_manager.set.call_args
            assert call_args[1]["ttl"] == 900  # 15 minutes
    
    @pytest.mark.asyncio
    async def test_retry_logic_on_transient_errors(
        self,
        carbon_api_client,
        mock_cache_manager,
        mock_electricity_maps_response
    ):
        """Test retry logic with exponential backoff."""
        mock_cache_manager.get.return_value = None
        
        call_count = 0
        
        async def mock_get_with_retry(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            
            mock_response = MagicMock()
            
            if call_count < 2:
                # First call fails
                mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                    "Temporary Error", request=MagicMock(), response=MagicMock()
                )
            else:
                # Second call succeeds
                mock_response.json.return_value = mock_electricity_maps_response
                mock_response.raise_for_status = MagicMock()
            
            return mock_response
        
        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = mock_get_with_retry
            
            result = await carbon_api_client.get_carbon_intensity(37.7749, -122.4194)
            
            assert result.carbon_intensity == 250.5
            assert call_count >= 2  # Verify retry happened
    
    @pytest.mark.asyncio
    async def test_api_without_credentials(self, mock_cache_manager):
        """Test that API calls fail gracefully without credentials."""
        client = CarbonAPIClient(
            cache_manager=mock_cache_manager,
            electricity_maps_api_key="",
            watttime_username="",
            watttime_password=""
        )
        
        mock_cache_manager.get.return_value = None
        
        # Should fall back to global average
        result = await client.get_carbon_intensity(37.7749, -122.4194)
        
        assert result.data_source == "fallback"
        assert result.carbon_intensity == 475.0
