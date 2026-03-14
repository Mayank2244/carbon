"""
Test script for Climatiq API integration.
Tests the carbon API client with all three providers.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.core.config import settings


async def test_carbon_api():
    """Test the carbon API client with fallback chain."""
    
    # Initialize cache manager
    cache_manager = CacheManager()
    
    # Initialize carbon API client
    client = CarbonAPIClient(cache_manager=cache_manager)
    
    print("=" * 60)
    print("Testing Carbon API Integration")
    print("=" * 60)
    
    # Test coordinates (San Francisco, CA)
    test_lat = 37.7749
    test_lon = -122.4194
    
    print(f"\nTest 1: Fetching carbon intensity for coordinates")
    print(f"Location: San Francisco ({test_lat}, {test_lon})")
    print("-" * 60)
    
    try:
        carbon_data = await client.get_carbon_intensity(test_lat, test_lon)
        print(f"✓ Success!")
        print(f"  Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        print(f"  Data Source: {carbon_data.data_source}")
        print(f"  Renewable %: {carbon_data.renewable_percentage:.1f}%")
        print(f"  Fossil Fuel %: {carbon_data.fossil_fuel_percentage:.1f}%")
        print(f"  Timestamp: {carbon_data.timestamp}")
        print(f"  Region: {carbon_data.region_code}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"Test 2: Fetching carbon intensity for region")
    print(f"Region: US-CA (California)")
    print("-" * 60)
    
    try:
        carbon_data = await client.get_region_carbon("US-CA")
        print(f"✓ Success!")
        print(f"  Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        print(f"  Data Source: {carbon_data.data_source}")
        print(f"  Renewable %: {carbon_data.renewable_percentage:.1f}%")
        print(f"  Fossil Fuel %: {carbon_data.fossil_fuel_percentage:.1f}%")
        print(f"  Timestamp: {carbon_data.timestamp}")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("API Configuration Status:")
    print("-" * 60)
    print(f"  Electricity Maps API: {'✓ Configured' if client.electricity_maps_api_key else '✗ Not configured'}")
    print(f"  WattTime API: {'✓ Configured' if client.watttime_username else '✗ Not configured'}")
    print(f"  Climatiq API: {'✓ Configured' if client.climatiq_api_key else '✗ Not configured'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_carbon_api())
