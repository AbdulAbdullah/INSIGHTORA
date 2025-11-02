#!/usr/bin/env python3
"""
Test login functionality
"""

import asyncio
import aiohttp
import json

async def test_login():
    try:
        # Test login
        login_data = {
            "email": "test@example.com",
            "password": "TestPassword123!",
            "remember_device": False,
            "device_name": "Test Login Device"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/auth/login",
                json=login_data
            ) as response:
                result = await response.json()
                print(f"Login Response Status: {response.status}")
                print(f"Login Response: {json.dumps(result, indent=2)}")
                
                if response.status == 200:
                    print("✅ Login successful!")
                    return result
                else:
                    print("❌ Login failed!")
                    return None
        
    except Exception as e:
        print(f"Error testing login: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_login())