"""
Script to validata accuracy of carbon data.
It fetches data from our API and compares it with known public values for specific regions.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.core.config import settings

async def validate_accuracy():
    print("=" * 80)
    print("CARBON DATA ACCURACY VALIDATION SCOUT")
    print("=" * 80)
    
    cache_manager = CacheManager()
    client = CarbonAPIClient(
        cache_manager=cache_manager,
        electricity_maps_api_key=settings.electricity_maps_api_key,
        climatiq_api_key=settings.climatiq_api_key
    )
    
    # Define benchmark regions with expected ranges based on public dashboards (e.g., Ember, Electricity Maps public map)
    # Ranges are approximate for validation purposes
    benchmarks = [
        {
            "name": "France", 
            "coords": (46.2276, 2.2137), 
            "code": "FR", 
            "expected_range": (0, 100), 
            "desc": "Low carbon (Nuclear)"
        },
        {
            "name": "Germany", 
            "coords": (51.1657, 10.4515), 
            "code": "DE", 
            "expected_range": (300, 700), 
            "desc": "Moderate-High (Coal/Renewables mix)"
        },
        {
            "name": "California", 
            "coords": (36.7783, -119.4179), 
            "code": "US-CAL-CISO", 
            "expected_range": (100, 350), 
            "desc": "Moderate (Gas/Solar mix)"
        },
        {
            "name": "Poland", 
            "coords": (51.9194, 19.1451), 
            "code": "PL", 
            "expected_range": (600, 900), 
            "desc": "High (Coal dominance)"
        }
    ]
    
    print(f"\n{'REGION':<15} {'SOURCE':<20} {'INTENSITY':<15} {'EXPECTED':<15} {'RESULT':<10}")
    print("-" * 80)
    
    for b in benchmarks:
        try:
            # Try region fetch first
            data = await client.get_region_carbon(b["code"])
            intensity = data.carbon_intensity
            source = data.data_source
            
            # Check if within expected range
            status = "✓ VALID" if b["expected_range"][0] <= intensity <= b["expected_range"][1] else "⚠️ CHECK"
            
            print(f"{b['name']:<15} {source:<20} {intensity:<15.1f} {str(b['expected_range']):<15} {status:<10}")
            
            if status != "✓ VALID":
                print(f"  Note: {b['desc']} - Value {intensity} outside approximate typical range.")
                
        except Exception as e:
            print(f"{b['name']:<15} ERROR: {str(e)}")

    print("-" * 80)
    print("\nMETHODOLOGY NOTEN:")
    print("1. Electricity Maps: Uses flow-tracing for consumption-based intensity (imports/exports included).")
    print("2. WattTime: Uses marginal emissions (impact of next unit of electricity).")
    print("3. Climatiq: Uses average emission factors (typically production-based).")
    print("\nIf 'source' is 'electricity_maps', data is real-time and consumption-based.")
    print("If 'source' is 'fallback', it defaults to global average (475 gCO2/kWh).")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(validate_accuracy())
