#!/usr/bin/env python3
"""
Test email service functionality
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

async def test_email_service():
    try:
        from app.core.email_service import email_service
        print(f"Email service instance: {email_service}")
        print(f"Email service type: {type(email_service)}")
        
        if email_service is None:
            print("ERROR: email_service is None!")
            return False
            
        # Test email configuration
        print(f"SMTP Host: {email_service.smtp_host}")
        print(f"SMTP User: {email_service.smtp_user}")
        print(f"Email From: {email_service.email_from}")
        
        # Test sending a registration OTP (this will actually send an email)
        print("Testing registration OTP email...")
        success = await email_service.send_registration_otp(
            email="test@example.com",
            name="Test User", 
            otp_code="123456"
        )
        
        print(f"Email send result: {success}")
        return success
        
    except Exception as e:
        print(f"Error testing email service: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(test_email_service())
    print(f"Test result: {result}")