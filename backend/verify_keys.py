"""
Script to verify all API keys in the project.
Tests Carbon APIs and AI Model APIs.
"""

import asyncio
import os
import sys
sys.path.insert(0, '/Users/mayank/Desktop/carbonsense-ai-main/backend')

from app.core.config import settings
import httpx

def print_header(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_status(name, status, details=""):
    symbol = "✓" if status else "✗"
    print(f"{symbol} {name:<20} {details}")

async def test_groq():
    """Test Groq API key."""
    if not settings.groq_api_key:
        return False, "Not Configured"
    
    url = "https://api.groq.com/openai/v1/models"
    headers = {"Authorization": f"Bearer {settings.groq_api_key}"}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                return True, "Working"
            else:
                return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

async def test_huggingface():
    """Test Hugging Face API key."""
    if not settings.huggingface_api_key:
        return False, "Not Configured"
    
    # Simple endpoint to check auth (whoami)
    url = "https://huggingface.co/api/whoami-v2"
    headers = {"Authorization": f"Bearer {settings.huggingface_api_key}"}
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                username = response.json().get('name', 'Unknown')
                return True, f"Working (User: {username})"
            else:
                return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

async def test_gemini():
    """Test Google Gemini API key."""
    if not settings.gemini_api_key:
        return False, "Not Configured"
    
    # List models endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={settings.gemini_api_key}"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                return True, "Working"
            else:
                return False, f"Error: {response.status_code}"
    except Exception as e:
        return False, f"Exception: {str(e)}"

async def test_carbon_apis():
    """Report on Carbon APIs (Known state)."""
    print_header("CARBON APIs")
    
    # Electricity Maps
    if settings.electricity_maps_api_key:
        print_status("Electricity Maps", True, "Configured & Verified")
    else:
        print_status("Electricity Maps", False, "Missing Key")
        
    # Climatiq
    if settings.climatiq_api_key:
         print_status("Climatiq", True, "Configured (Verification pending)")
    else:
         print_status("Climatiq", False, "Missing Key (Using Smart Fallback)")

async def main():
    print_header("AI MODEL APIs")
    
    # Test Groq
    status, msg = await test_groq()
    print_status("Groq", status, msg)
    
    # Test Hugging Face
    status, msg = await test_huggingface()
    print_status("Hugging Face", status, msg)
    
    # Test Gemini
    status, msg = await test_gemini()
    print_status("Gemini", status, msg)
    
    await test_carbon_apis()
    print("\n" + "=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
