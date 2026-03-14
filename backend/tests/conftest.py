"""Pytest configuration and fixtures for Carbon API tests."""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any

from app.modules.cache_manager import CacheManager
from app.modules.carbon_api import CarbonAPIClient, CarbonData


@pytest.fixture
def mock_cache_manager():
    """Mock CacheManager for testing."""
    cache = AsyncMock(spec=CacheManager)
    cache.get = AsyncMock(return_value=None)
    cache.set = AsyncMock(return_value=True)
    return cache


@pytest.fixture
def carbon_api_client(mock_cache_manager):
    """Create CarbonAPIClient instance for testing."""
    return CarbonAPIClient(
        cache_manager=mock_cache_manager,
        electricity_maps_api_key="test_em_key",
        watttime_username="test_user",
        watttime_password="test_pass"
    )


@pytest.fixture
def mock_electricity_maps_response() -> Dict[str, Any]:
    """Mock Electricity Maps API response."""
    return {
        "zone": "US-CA",
        "carbonIntensity": 250.5,
        "datetime": "2024-01-08T10:00:00Z",
        "updatedAt": "2024-01-08T10:05:00Z",
        "fossilFuelPercentage": 35.2,
        "renewablePercentage": 64.8
    }


@pytest.fixture
def mock_watttime_response() -> Dict[str, Any]:
    """Mock WattTime API response."""
    return {
        "ba": "CAISO_NORTH",
        "moer": 1200.5,  # lbs CO2/MWh
        "percent": 45.0,
        "point_time": "2024-01-08T10:00:00Z"
    }


@pytest.fixture
def mock_watttime_login_response() -> Dict[str, Any]:
    """Mock WattTime login response."""
    return {
        "token": "mock_jwt_token_12345"
    }


@pytest.fixture
def sample_carbon_data() -> CarbonData:
    """Sample CarbonData object for testing."""
    return CarbonData(
        carbon_intensity=250.5,
        renewable_percentage=64.8,
        fossil_fuel_percentage=35.2,
        timestamp=datetime(2024, 1, 8, 10, 0, 0),
        data_source="electricity_maps",
        region_code="US-CA",
        latitude=37.7749,
        longitude=-122.4194
    )
