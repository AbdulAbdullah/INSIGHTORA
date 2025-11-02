#!/usr/bin/env python3
"""
Get the latest OTP for testing
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

async def get_latest_otp():
    try:
        from app.core.database import get_async_db
        from app.modules.auth.models import OTPVerification
        from sqlalchemy import select, desc
        
        async for db in get_async_db():
            # Get the latest OTP
            result = await db.execute(
                select(OTPVerification)
                .where(OTPVerification.is_used == False)
                .where(OTPVerification.is_expired == False)
                .order_by(desc(OTPVerification.created_at))
                .limit(1)
            )
            otp = result.scalar_one_or_none()
            
            if otp:
                print(f"Latest OTP: {otp.otp_code}")
                print(f"Type: {otp.otp_type}")
                print(f"User ID: {otp.user_id}")
                print(f"Expires at: {otp.expires_at}")
                return otp.otp_code
            else:
                print("No active OTP found")
                return None
            break
        
    except Exception as e:
        print(f"Error getting OTP: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    otp = asyncio.run(get_latest_otp())
    print(f"OTP Code: {otp}")