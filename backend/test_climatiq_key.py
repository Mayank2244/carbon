"""
Test Climatiq Key Validity
"""
import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')
from app.core.config import settings
from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient

async def test_climatiq():
    print(f"Testing Climatiq Key: {settings.climatiq_api_key}")
    cache_manager = CacheManager()
    client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=None,
        climatiq_api_key=settings.climatiq_api_key 
    )
    # Force EM key to None (bypass settings)
    client.electricity_maps_api_key = None 
    
    try:
        # Try to fetch France (uses Climatiq if EM key is None)
        # Note: CarbonAPIClient falls back to static if it fails.
        # We need to check the data_source in the response.
        data = await client.get_carbon_intensity(48.8566, 2.3522)
        print(f"Result Source: {data.data_source}")
        if data.data_source == "climatiq":
            print("✓ Climatiq Key is VALID")
        else:
            print("✗ Climatiq Key is INVALID or Quota Exceeded (Fell back to static)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_climatiq())
