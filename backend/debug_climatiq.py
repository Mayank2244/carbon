import asyncio
import httpx
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')
from app.core.config import settings

async def debug_call():
    key = settings.climatiq_api_key
    print(f"Key: {key}")
    
    url = "https://api.climatiq.io/data/v1/estimate"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    # Try 1: Remove year (let it find most recent)
    payload1 = {
        "emission_factor": {
            "activity_id": "electricity-supply_grid-source_supplier_mix",
            "region": "US"
        },
        "parameters": {
            "energy": 1,
            "energy_unit": "kWh"
        }
    }
    
    print("\nAttempt 1 (No Year):")
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, headers=headers, json=payload1)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text}")

    # Try 2: Different Activity ID (Generic match)
    # Search for an emission factor first
    search_url = "https://api.climatiq.io/data/v1/search"
    print("\nAttempt 2 (Search for valid ID):")
    async with httpx.AsyncClient() as client:
        resp = await client.get(search_url, headers=headers, params={"query": "electricity", "region": "US"})
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            print(f"First Result: {resp.json()['results'][0] if resp.json()['results'] else 'None'}")
        else:
            print(f"Response: {resp.text}")

if __name__ == "__main__":
    asyncio.run(debug_call())
