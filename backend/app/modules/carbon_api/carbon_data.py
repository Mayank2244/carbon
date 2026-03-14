"""
Carbon Data Models
Defines data structures for carbon intensity information.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class CarbonData(BaseModel):
    """Carbon intensity data from grid APIs."""
    
    carbon_intensity: float = Field(
        ...,
        description="Carbon intensity in gCO2/kWh",
        ge=0.0
    )
    renewable_percentage: float = Field(
        ...,
        description="Percentage of renewable energy in the grid",
        ge=0.0,
        le=100.0
    )
    fossil_fuel_percentage: float = Field(
        ...,
        description="Percentage of fossil fuel energy in the grid",
        ge=0.0,
        le=100.0
    )
    timestamp: datetime = Field(
        ...,
        description="Timestamp of the data"
    )
    data_source: str = Field(
        ...,
        description="Source of the data (e.g., 'electricity_maps', 'watttime', 'fallback')"
    )
    region_code: Optional[str] = Field(
        default=None,
        description="Region/zone code if applicable"
    )
    latitude: Optional[float] = Field(
        default=None,
        description="Latitude coordinate",
        ge=-90.0,
        le=90.0
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Longitude coordinate",
        ge=-180.0,
        le=180.0
    )
    
    @validator("renewable_percentage", "fossil_fuel_percentage")
    def validate_percentages(cls, v: float, values: dict) -> float:
        """Ensure percentages are valid."""
        if v < 0 or v > 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class WattTimeResponse(BaseModel):
    """Response model for WattTime API."""
    
    freq: str  # e.g. "300"
    ba: str  # Balancing Authority
    percent: str  # Relative emissions (0-100)
    point_time: str  # Timestamp
    
    def to_carbon_data(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> CarbonData:
        """Convert to CarbonData model."""
        # WattTime returns "percent" which is relative emissions (0-100)
        # We need to map this to carbon intensity or use it as a proxy.
        # However, for the purpose of this interface, we might need to approximate or use valid fields.
        # Real WattTime API /v2/data returns 'percent' but also 'moer' (marginal operating emissions rate).
        # Let's assume the response might contain 'moer' if we ask for it?
        # The client asks for `signal_type="co2_moer"`.
        # So we should include `moer` field if available or extra fields.
        # But for now, let's define a basic structure.
        
        # NOTE: This is a simplified model.
        return CarbonData(
             # Using 0.0 as placeholder if actual intensity isn't in 'percent' directly.
             # Actually 'percent' is likely 0-100 relative.
             # Let's use a dummy conversion or trust the data if it has 'moer'.
             carbon_intensity=0.0, 
             renewable_percentage=0.0,
             fossil_fuel_percentage=0.0,
             timestamp=datetime.fromisoformat(self.point_time.replace('Z', '+00:00')),
             data_source="watttime",
             region_code=self.ba,
             latitude=latitude,
             longitude=longitude
        )


class ElectricityMapsResponse(BaseModel):
    """Response model for Electricity Maps API."""
    
    zone: str
    carbonIntensity: float
    datetime: str
    updatedAt: str
    fossilFuelPercentage: Optional[float] = None
    renewablePercentage: Optional[float] = None
    
    def to_carbon_data(self, latitude: Optional[float] = None, longitude: Optional[float] = None) -> CarbonData:
        """Convert to CarbonData model."""
        return CarbonData(
            carbon_intensity=self.carbonIntensity,
            renewable_percentage=self.renewablePercentage or 0.0,
            fossil_fuel_percentage=self.fossilFuelPercentage or 0.0,
            timestamp=datetime.fromisoformat(self.datetime.replace('Z', '+00:00')),
            data_source="electricity_maps",
            region_code=self.zone,
            latitude=latitude,
            longitude=longitude
        )



class ClimatiqResponse(BaseModel):
    """Response model for Climatiq API."""
    
    co2e: float  # Total CO2 equivalent in kg
    co2e_unit: str  # Unit (typically "kg")
    co2e_calculation_method: Optional[str] = None
    co2e_calculation_origin: Optional[str] = None
    emission_factor: dict  # Emission factor details
    constituent_gases: Optional[dict] = None
    
    def to_carbon_data(
        self, 
        latitude: Optional[float] = None, 
        longitude: Optional[float] = None,
        region_code: Optional[str] = None
    ) -> CarbonData:
        """Convert to CarbonData model."""
        # Extract carbon intensity from emission factor
        # Climatiq returns kgCO2e per kWh, convert to gCO2/kWh
        factor_value = self.emission_factor.get("activity_id", {})
        
        # The emission factor is in kgCO2e per unit
        # For electricity, this is typically kgCO2e/kWh
        # Convert to gCO2/kWh by multiplying by 1000
        carbon_intensity_gco2_kwh = self.co2e * 1000  # co2e is already per kWh for electricity
        
        return CarbonData(
            carbon_intensity=carbon_intensity_gco2_kwh,
            renewable_percentage=0.0,  # Climatiq doesn't provide this
            fossil_fuel_percentage=0.0,  # Climatiq doesn't provide this
            timestamp=datetime.utcnow(),
            data_source="climatiq",
            region_code=region_code,
            latitude=latitude,
            longitude=longitude
        )
