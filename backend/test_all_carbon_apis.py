"""
Comprehensive test for all Carbon API layers.
Tests individual APIs and fallback chain combinations.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.core.config import settings


def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(success, data=None, error=None):
    """Print test result."""
    if success:
        print(f"✓ SUCCESS")
        if data:
            print(f"  Carbon Intensity: {data.carbon_intensity:.2f} gCO2/kWh")
            print(f"  Data Source: {data.data_source}")
            print(f"  Renewable %: {data.renewable_percentage:.1f}%")
            print(f"  Fossil Fuel %: {data.fossil_fuel_percentage:.1f}%")
            print(f"  Region: {data.region_code or 'N/A'}")
            print(f"  Timestamp: {data.timestamp}")
    else:
        print(f"✗ FAILED: {error}")


async def test_individual_apis():
    """Test each API individually."""
    cache_manager = CacheManager()
    
    print_header("INDIVIDUAL API TESTS")
    
    # Test coordinates
    test_coords = [
        ("San Francisco, CA", 37.7749, -122.4194),
        ("New York, NY", 40.7128, -74.0060),
        ("London, UK", 51.5074, -0.1278),
        ("Tokyo, Japan", 35.6762, 139.6503),
    ]
    
    # Test 1: Electricity Maps Only
    print("\n" + "-" * 70)
    print("TEST 1: Electricity Maps API (Primary)")
    print("-" * 70)
    
    em_client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=settings.electricity_maps_api_key,
        watttime_username=None,
        watttime_password=None,
        climatiq_api_key=None
    )
    # Ensure others are disabled
    em_client.watttime_username = None
    em_client.climatiq_api_key = None
    
    for location, lat, lon in test_coords:
        print(f"\n  Location: {location} ({lat}, {lon})")
        try:
            data = await em_client.get_carbon_intensity(lat, lon)
            print_result(True, data)
        except Exception as e:
            print_result(False, error=str(e))
    
    # Test 2: WattTime Only
    print("\n" + "-" * 70)
    print("TEST 2: WattTime API (Secondary)")
    print("-" * 70)
    
    wt_client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=None,
        watttime_username=settings.watttime_username,
        watttime_password=settings.watttime_password,
        climatiq_api_key=None
    )
    # Ensure others are disabled
    wt_client.electricity_maps_api_key = None
    wt_client.climatiq_api_key = None
    
    for location, lat, lon in test_coords[:2]:  # Test only US locations
        print(f"\n  Location: {location} ({lat}, {lon})")
        try:
            data = await wt_client.get_carbon_intensity(lat, lon)
            print_result(True, data)
        except Exception as e:
            print_result(False, error=str(e))
    
    # Test 3: Climatiq Only
    print("\n" + "-" * 70)
    print("TEST 3: Climatiq API (Tertiary)")
    print("-" * 70)
    
    cq_client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=None,
        watttime_username=None,
        watttime_password=None,
        climatiq_api_key=settings.climatiq_api_key
    )
    # Ensure others are disabled
    cq_client.electricity_maps_api_key = None
    cq_client.watttime_username = None
    
    for location, lat, lon in test_coords:
        print(f"\n  Location: {location} ({lat}, {lon})")
        try:
            data = await cq_client.get_carbon_intensity(lat, lon)
            print_result(True, data)
        except Exception as e:
            print_result(False, error=str(e))


async def test_fallback_chain():
    """Test the complete fallback chain."""
    cache_manager = CacheManager()
    
    print_header("FALLBACK CHAIN TESTS")
    
    # Test scenarios
    scenarios = [
        {
            "name": "All APIs Enabled",
            "em_key": settings.electricity_maps_api_key,
            "wt_user": settings.watttime_username,
            "wt_pass": settings.watttime_password,
            "cq_key": settings.climatiq_api_key,
        },
        {
            "name": "Only Electricity Maps + Climatiq",
            "em_key": settings.electricity_maps_api_key,
            "wt_user": None,
            "wt_pass": None,
            "cq_key": settings.climatiq_api_key,
        },
        {
            "name": "Only WattTime + Climatiq",
            "em_key": None,
            "wt_user": settings.watttime_username,
            "wt_pass": settings.watttime_password,
            "cq_key": settings.climatiq_api_key,
        },
        {
            "name": "Only Climatiq",
            "em_key": None,
            "wt_user": None,
            "wt_pass": None,
            "cq_key": settings.climatiq_api_key,
        },
        {
            "name": "No APIs (Fallback Only)",
            "em_key": None,
            "wt_user": None,
            "wt_pass": None,
            "cq_key": None,
        },
    ]
    
    test_location = ("San Francisco, CA", 37.7749, -122.4194)
    
    for scenario in scenarios:
        print("\n" + "-" * 70)
        print(f"SCENARIO: {scenario['name']}")
        print("-" * 70)
        
        client = CarbonAPIClient(
            cache_manager=cache_manager,
            electricity_maps_api_key=scenario['em_key'],
            watttime_username=scenario['wt_user'],
            watttime_password=scenario['wt_pass'],
            climatiq_api_key=scenario['cq_key']
        )
        
        # FORCE override to ensure settings don't bleed through
        if scenario['em_key'] is None:
            client.electricity_maps_api_key = None
        if scenario['wt_user'] is None:
            client.watttime_username = None
        if scenario['cq_key'] is None:
            client.climatiq_api_key = None
        
        location, lat, lon = test_location
        print(f"\n  Location: {location} ({lat}, {lon})")
        
        try:
            data = await client.get_carbon_intensity(lat, lon)
            print_result(True, data)
            
            # Show which API was used
            if data.data_source == "electricity_maps":
                print("  → Used: Electricity Maps (Primary)")
            elif data.data_source == "watttime":
                print("  → Used: WattTime (Secondary)")
            elif data.data_source == "climatiq":
                print("  → Used: Climatiq (Tertiary)")
            elif data.data_source == "fallback":
                print("  → Used: Global Average Fallback")
                
        except Exception as e:
            print_result(False, error=str(e))


async def test_region_queries():
    """Test region-based queries."""
    cache_manager = CacheManager()
    
    print_header("REGION-BASED QUERY TESTS")
    
    client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=settings.electricity_maps_api_key,
        watttime_username=settings.watttime_username,
        watttime_password=settings.watttime_password,
        climatiq_api_key=settings.climatiq_api_key
    )
    
    test_regions = [
        ("US-CAL-CISO", "California ISO"),
        ("DE", "Germany"),
        ("GB", "United Kingdom"),
        ("FR", "France"),
    ]
    
    for region_code, region_name in test_regions:
        print("\n" + "-" * 70)
        print(f"Region: {region_name} ({region_code})")
        print("-" * 70)
        
        try:
            data = await client.get_region_carbon(region_code)
            print_result(True, data)
            print(f"  → Data Source: {data.data_source}")
        except Exception as e:
            print_result(False, error=str(e))


async def test_api_status():
    """Display API configuration status."""
    cache_manager = CacheManager()
    client = CarbonAPIClient(cache_manager=cache_manager)
    
    print_header("API CONFIGURATION STATUS")
    
    print("\n  API Provider Status:")
    print("  " + "-" * 66)
    
    # Electricity Maps
    em_status = "✓ CONFIGURED" if client.electricity_maps_api_key else "✗ NOT CONFIGURED"
    em_key_preview = f"({client.electricity_maps_api_key[:8]}...)" if client.electricity_maps_api_key else ""
    print(f"  Electricity Maps:  {em_status} {em_key_preview}")
    
    # WattTime
    wt_status = "✓ CONFIGURED" if client.watttime_username else "✗ NOT CONFIGURED"
    wt_user_preview = f"({client.watttime_username})" if client.watttime_username else ""
    print(f"  WattTime:          {wt_status} {wt_user_preview}")
    
    # Climatiq
    cq_status = "✓ CONFIGURED" if client.climatiq_api_key else "✗ NOT CONFIGURED"
    cq_key_preview = f"({client.climatiq_api_key[:8]}...)" if client.climatiq_api_key else ""
    print(f"  Climatiq:          {cq_status} {cq_key_preview}")
    
    print("\n  Fallback Chain Order:")
    print("  " + "-" * 66)
    print("  1. Electricity Maps (Real-time, high accuracy)")
    print("  2. WattTime (Real-time, US-focused)")
    print("  3. Climatiq (Emission factors, global coverage)")
    print("  4. Global Average (475 gCO2/kWh)")
    
    print("\n  Cache Configuration:")
    print("  " + "-" * 66)
    print(f"  Cache TTL: {settings.carbon_cache_ttl} seconds ({settings.carbon_cache_ttl // 60} minutes)")


async def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  CARBON API COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    # Display API status first
    await test_api_status()
    
    # Run individual API tests
    await test_individual_apis()
    
    # Run fallback chain tests
    await test_fallback_chain()
    
    # Run region-based tests
    await test_region_queries()
    
    print("\n" + "=" * 70)
    print("  TEST SUITE COMPLETE")
    print("=" * 70)
    print()


if __name__ == "__main__":
    asyncio.run(main())
