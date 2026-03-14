"""
Example usage of Carbon API Client.
Demonstrates how to use the CarbonAPIClient to fetch carbon intensity data.
"""

import asyncio
from datetime import datetime

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.modules.cache_manager import CacheManager
from app.modules.carbon_api import CarbonAPIClient, CarbonData
from app.db.redis import init_redis, close_redis

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def example_coordinate_query():
    """Example: Get carbon intensity by coordinates."""
    logger.info("=" * 60)
    logger.info("Example 1: Query by Coordinates")
    logger.info("=" * 60)
    
    # Initialize cache manager and API client
    cache_manager = CacheManager()
    carbon_client = CarbonAPIClient(cache_manager=cache_manager)
    
    # San Francisco coordinates
    latitude = 37.7749
    longitude = -122.4194
    
    logger.info(f"Fetching carbon intensity for San Francisco ({latitude}, {longitude})")
    
    try:
        carbon_data = await carbon_client.get_carbon_intensity(latitude, longitude)
        
        logger.info(f"✓ Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        logger.info(f"✓ Renewable Energy: {carbon_data.renewable_percentage:.1f}%")
        logger.info(f"✓ Fossil Fuel: {carbon_data.fossil_fuel_percentage:.1f}%")
        logger.info(f"✓ Data Source: {carbon_data.data_source}")
        logger.info(f"✓ Timestamp: {carbon_data.timestamp}")
        
        if carbon_data.region_code:
            logger.info(f"✓ Region: {carbon_data.region_code}")
        
        return carbon_data
        
    except Exception as e:
        logger.error(f"✗ Error fetching carbon data: {str(e)}")
        raise


async def example_region_query():
    """Example: Get carbon intensity by region code."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Query by Region Code")
    logger.info("=" * 60)
    
    cache_manager = CacheManager()
    carbon_client = CarbonAPIClient(cache_manager=cache_manager)
    
    region_code = "US-CAL-CISO"  # California (CISO)
    
    logger.info(f"Fetching carbon intensity for region: {region_code}")
    
    try:
        carbon_data = await carbon_client.get_region_carbon(region_code)
        
        logger.info(f"✓ Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        logger.info(f"✓ Renewable Energy: {carbon_data.renewable_percentage:.1f}%")
        logger.info(f"✓ Fossil Fuel: {carbon_data.fossil_fuel_percentage:.1f}%")
        logger.info(f"✓ Data Source: {carbon_data.data_source}")
        logger.info(f"✓ Region: {carbon_data.region_code}")
        
        return carbon_data
        
    except Exception as e:
        logger.error(f"✗ Error fetching carbon data: {str(e)}")
        raise


async def example_cache_behavior():
    """Example: Demonstrate cache hit behavior."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Cache Behavior")
    logger.info("=" * 60)
    
    cache_manager = CacheManager()
    carbon_client = CarbonAPIClient(cache_manager=cache_manager)
    
    latitude = 37.7749
    longitude = -122.4194
    
    # First call - cache miss
    logger.info("First call (cache miss expected):")
    start_time = datetime.now()
    carbon_data_1 = await carbon_client.get_carbon_intensity(latitude, longitude)
    elapsed_1 = (datetime.now() - start_time).total_seconds()
    logger.info(f"✓ Completed in {elapsed_1:.3f} seconds")
    logger.info(f"✓ Data source: {carbon_data_1.data_source}")
    
    # Second call - cache hit
    logger.info("\nSecond call (cache hit expected):")
    start_time = datetime.now()
    carbon_data_2 = await carbon_client.get_carbon_intensity(latitude, longitude)
    elapsed_2 = (datetime.now() - start_time).total_seconds()
    logger.info(f"✓ Completed in {elapsed_2:.3f} seconds")
    logger.info(f"✓ Data source: {carbon_data_2.data_source}")
    
    logger.info(f"\n✓ Cache speedup: {elapsed_1 / elapsed_2:.1f}x faster")


async def example_error_handling():
    """Example: Demonstrate error handling and fallback."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 4: Error Handling")
    logger.info("=" * 60)
    
    cache_manager = CacheManager()
    
    # Create client with invalid credentials to trigger fallback
    carbon_client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key="",
        watttime_username="",
        watttime_password=""
    )
    
    logger.info("Attempting to fetch data with invalid credentials...")
    
    try:
        carbon_data = await carbon_client.get_carbon_intensity(37.7749, -122.4194)
        
        logger.info(f"✓ Fallback data returned successfully")
        logger.info(f"✓ Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh (global average)")
        logger.info(f"✓ Data Source: {carbon_data.data_source}")
        
    except Exception as e:
        logger.error(f"✗ Unexpected error: {str(e)}")


async def example_multiple_locations():
    """Example: Query multiple locations."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 5: Multiple Locations")
    logger.info("=" * 60)
    
    cache_manager = CacheManager()
    carbon_client = CarbonAPIClient(cache_manager=cache_manager)
    
    locations = [
        {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
        {"name": "New York", "lat": 40.7128, "lon": -74.0060},
        {"name": "London", "lat": 51.5074, "lon": -0.1278},
        {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    ]
    
    results = []
    
    for location in locations:
        try:
            logger.info(f"\nFetching data for {location['name']}...")
            carbon_data = await carbon_client.get_carbon_intensity(
                location['lat'],
                location['lon']
            )
            
            results.append({
                "location": location['name'],
                "carbon_intensity": carbon_data.carbon_intensity,
                "renewable_percentage": carbon_data.renewable_percentage,
                "data_source": carbon_data.data_source
            })
            
            logger.info(f"✓ {location['name']}: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
            
        except Exception as e:
            logger.error(f"✗ Error for {location['name']}: {str(e)}")
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    logger.info("=" * 60)
    
    for result in results:
        logger.info(
            f"{result['location']:15} | "
            f"{result['carbon_intensity']:6.1f} gCO2/kWh | "
            f"{result['renewable_percentage']:5.1f}% renewable | "
            f"Source: {result['data_source']}"
        )


async def main():
    """Run all examples."""
    logger.info("Carbon API Client - Example Usage")
    logger.info("=" * 60)
    
    # Initialize Redis
    await init_redis()
    
    try:
        # Run examples
        await example_coordinate_query()
        await example_region_query()
        await example_cache_behavior()
        await example_error_handling()
        await example_multiple_locations()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ All examples completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Example failed: {str(e)}")
        raise
    finally:
        await close_redis()


if __name__ == "__main__":
    asyncio.run(main())
