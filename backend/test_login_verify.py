#!/usr/bin/env python3
"""
Test login verification functionality
"""

import asyncio
import aiohttp
import json

async def test_login_verify():
    try:
        # Test login verification
        verify_data = {
            "email": "test@example.com",
            "otp_code": "737328",
            "otp_type": "login",
            "remember_device": True,
            "device_name": "Test Login Device"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "http://localhost:8000/api/v1/auth/verify-login",
                json=verify_data
            ) as response:
                result = await response.json()
                print(f"Login Verify Response Status: {response.status}")
                print(f"Login Verify Response: {json.dumps(result, indent=2)}")
                
                if response.status == 200:
                    print("✅ Login verification successful!")
                    print(f"✅ Access Token: {result.get('access_token', 'N/A')[:50]}...")
                    print(f"✅ User ID: {result.get('user', {}).get('id', 'N/A')}")
                    print(f"✅ User Email: {result.get('user', {}).get('email', 'N/A')}")
                    return result
                else:
                    print("❌ Login verification failed!")
                    return None
        
    except Exception as e:
        print(f"Error testing login verification: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_login_verify())