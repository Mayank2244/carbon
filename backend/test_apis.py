"""
Comprehensive API integration test script.
Tests all external APIs: Groq, Hugging Face, Gemini, Electricity Maps, Climatiq.
"""

import asyncio
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.modules.model_selector.api_integrations import APIIntegrations
from app.modules.cache_manager import CacheManager
from app.modules.carbon_api.carbon_api_client import CarbonAPIClient
from app.core.config import settings


async def test_groq_api():
    """Test Groq API integration."""
    print("\n" + "=" * 60)
    print("Testing Groq API")
    print("=" * 60)
    
    api = APIIntegrations()
    
    if not api.groq_client:
        print("✗ Groq API key not configured")
        return False
    
    try:
        response = await api.call_groq(
            model="llama-3.1-8b-instant",
            prompt="What is 2+2? Answer in one sentence.",
            max_tokens=50
        )
        print(f"✓ Groq API working!")
        print(f"  Model: {response.model_name}")
        print(f"  Response: {response.text[:100]}...")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Latency: {response.latency_ms:.0f}ms")
        return True
    except Exception as e:
        print(f"✗ Groq API failed: {str(e)}")
        return False


async def test_huggingface_api():
    """Test Hugging Face API integration."""
    print("\n" + "=" * 60)
    print("Testing Hugging Face API")
    print("=" * 60)
    
    api = APIIntegrations()
    
    if not api.hf_client:
        print("✗ Hugging Face API key not configured")
        return False
    
    try:
        # Use a non-gated, reliable model for testing
        response = await api.call_huggingface(
            model="HuggingFaceH4/zephyr-7b-beta",
            prompt="What is 2+2? Answer in one sentence.",
            max_tokens=50
        )
        print(f"✓ Hugging Face API working!")
        print(f"  Model: {response.model_name}")
        print(f"  Response: {response.text[:100]}...")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Latency: {response.latency_ms:.0f}ms")
        return True
    except Exception as e:
        print(f"✗ Hugging Face API failed: {str(e)}")
        return False


async def test_electricity_maps():
    """Test Electricity Maps API."""
    print("\n" + "=" * 60)
    print("Testing Electricity Maps API")
    print("=" * 60)
    
    cache_manager = CacheManager()
    client = CarbonAPIClient(cache_manager=cache_manager)
    
    if not client.electricity_maps_api_key:
        print("✗ Electricity Maps API key not configured")
        return False
    
    try:
        # Test with San Francisco coordinates
        carbon_data = await client.get_carbon_intensity(37.7749, -122.4194)
        print(f"✓ Electricity Maps API working!")
        print(f"  Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        print(f"  Data Source: {carbon_data.data_source}")
        print(f"  Renewable %: {carbon_data.renewable_percentage:.1f}%")
        return True
    except Exception as e:
        print(f"✗ Electricity Maps API failed: {str(e)}")
        return False


async def test_climatiq():
    """Test Climatiq API."""
    print("\n" + "=" * 60)
    print("Testing Climatiq API")
    print("=" * 60)
    
    cache_manager = CacheManager()
    client = CarbonAPIClient(cache_manager=cache_manager)
    
    if not client.climatiq_api_key:
        print("✗ Climatiq API key not configured")
        return False
    
    try:
        carbon_data = await client._fetch_region_from_climatiq("US")
        print(f"✓ Climatiq API working!")
        print(f"  Carbon Intensity: {carbon_data.carbon_intensity:.2f} gCO2/kWh")
        print(f"  Data Source: {carbon_data.data_source}")
        return True
    except Exception as e:
        print(f"✗ Climatiq API failed: {str(e)}")
        return False


async def test_gemini_api():
    """Test Gemini API integration."""
    print("\n" + "=" * 60)
    print("Testing Gemini API")
    print("=" * 60)
    
    api = APIIntegrations()
    
    if not api.has_gemini:
        print("✗ Gemini API key not configured")
        return False
    
    try:
        # Use a model that is definitely available (based on debug output)
        response = await api.call_gemini(
            model="gemini-2.0-flash",
            prompt="What is 2+2? Answer in one sentence.",
            max_tokens=50
        )
        print(f"✓ Gemini API working!")
        print(f"  Model: {response.model_name}")
        print(f"  Response: {response.text[:100]}...")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Latency: {response.latency_ms:.0f}ms")
        return True
    except Exception as e:
        print(f"✗ Gemini API failed: {str(e)}")
        return False


async def main():
    """Run all API tests."""
    print("\n" + "=" * 60)
    print("CarbonSense AI - External API Integration Tests")
    print("=" * 60)
    
    results = {}
    
    # Test AI Model APIs
    results['Groq'] = await test_groq_api()
    results['Hugging Face'] = await test_huggingface_api()
    results['Gemini'] = await test_gemini_api()
    
    # Test Carbon APIs
    results['Electricity Maps'] = await test_electricity_maps()
    results['Climatiq'] = await test_climatiq()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for api_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {api_name:20s} {status}")
    
    print("\n" + "=" * 60)
    total = len(results)
    passed = sum(results.values())
    print(f"Total: {passed}/{total} APIs working")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
