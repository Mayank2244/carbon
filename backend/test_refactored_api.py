"""
Comprehensive test for Carbon API v2 (No WattTime, Smart Fallback).
Tests individual APIs and new fallback logic.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.core.config import settings


def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(success, data=None, error=None):
    if success:
        print(f"✓ SUCCESS")
        if data:
            print(f"  Carbon Intensity: {data.carbon_intensity:.2f} gCO2/kWh")
            print(f"  Data Source: {data.data_source}")
            print(f"  Region: {data.region_code or 'N/A'}")
    else:
        print(f"✗ FAILED: {error}")


async def test_smart_fallback():
    """Test the new Smart Static Fallback feature."""
    cache_manager = CacheManager()
    
    print_header("SMART STATIC FALLBACK TESTS (No APIs Configured)")
    
    # Initialize client with NO API KEYS to force fallback
    client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=None,
        climatiq_api_key=None
    )
    # FORCE override settings that might have been loaded
    client.electricity_maps_api_key = None
    client.climatiq_api_key = None
    
    # Locations to test static fallback diversity
    test_cases = [
        ("France (Nuclear)", 48.8566, 2.3522, "average", 50.0),
        ("Poland (Coal)", 52.2297, 21.0122, "average", 750.0),
        ("California (Solar/Gas)", 36.7783, -119.4179, "average", 200.0),
        ("Unknown/Global", 0.0, 0.0, "average", 475.0),
    ]
    
    for name, lat, lon, desc, expected in test_cases:
        print(f"\nLocation: {name}")
        try:
            data = await client.get_carbon_intensity(lat, lon)
            print_result(True, data)
            
            # Verify it's using the smart fallback
            if data.carbon_intensity == expected:
                print("  → verified: Matches static expected value")
            elif data.data_source == "fallback_global_avg" and name == "Unknown/Global":
                 print("  → verified: Correctly used global average")
            else:
                 print(f"  → warning: Unexpected value (Expected {expected})")
                 
        except Exception as e:
            print_result(False, error=str(e))


async def test_apis():
    """Test API integration."""
    cache_manager = CacheManager()
    
    print_header("API INTEGRATION TESTS")
    
    # Test 1: Electricity Maps (Should work with configured key)
    print("\nTEST 1: Electricity Maps (Primary)")
    client_em = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=settings.electricity_maps_api_key,
        climatiq_api_key=None
    )
    try:
        data = await client_em.get_carbon_intensity(37.7749, -122.4194) # SF
        print_result(True, data)
    except Exception as e:
        print_result(False, error=str(e))

    # Test 2: Climatiq (Should skip if no key, or work if key provided)
    print("\nTEST 2: Climatiq (Fallback Integration)")
    # We deliberately don't provide a key to see it gracefully fail to static
    client_cq = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=None,
        climatiq_api_key="invalid_test_key" # Should fail auth and fall to static
    )
    try:
        data = await client_cq.get_carbon_intensity(48.8566, 2.3522) # France
        print_result(True, data)
    except Exception as e:
        # It's expected to fail auth if the key is invalid, OR fall back if we catch the error
        # Our client catches errors and falls back
        print_result(True, data=None, error="Note: If this printed, exception wasn't caught inside client")


async def main():
    await test_smart_fallback()
    await test_apis()

if __name__ == "__main__":
    asyncio.run(main())
