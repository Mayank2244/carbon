import asyncio
import httpx
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')
from app.core.config import settings

async def debug_call():
    key = settings.climatiq_api_key
    url = "https://api.climatiq.io/data/v1/estimate"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Try with data_version
    payload = {
        "emission_factor": {
            "activity_id": "electricity-supply_grid-source_supplier_mix",
            "region": "US",
            "data_version": "^30" 
        },
        "parameters": {
            "energy": 1,
            "energy_unit": "kWh"
        }
    }
    
    print("\nAttempt with data_version:")
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(debug_call())
