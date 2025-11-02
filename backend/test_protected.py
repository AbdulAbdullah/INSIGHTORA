#!/usr/bin/env python3
"""
Test protected endpoint with JWT token
"""

import asyncio
import aiohttp
import json

async def test_protected_endpoint():
    try:
        # Use the access token from login verification
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZW1haWwiOiJ0ZXN0QGV4YW1wbGUuY29tIiwic2NvcGVzIjpbInVzZXIiXSwiZXhwIjoxNzYyMDg3NzYzLCJ0eXBlIjoiYWNjZXNzIn0.qP8K_9jjNq4cfUks-YADCKkeQpISFtgkGslmLBjGzV8"
        
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:8000/api/v1/auth/me",
                headers=headers
            ) as response:
                result = await response.json()
                print(f"Protected Endpoint Response Status: {response.status}")
                print(f"Protected Endpoint Response: {json.dumps(result, indent=2)}")
                
                if response.status == 200:
                    print("✅ Protected endpoint access successful!")
                    print(f"✅ Current User: {result.get('name', 'N/A')} ({result.get('email', 'N/A')})")
                    return result
                else:
                    print("❌ Protected endpoint access failed!")
                    return None
        
    except Exception as e:
        print(f"Error testing protected endpoint: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_protected_endpoint())