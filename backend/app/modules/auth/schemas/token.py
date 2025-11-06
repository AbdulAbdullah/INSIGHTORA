"""
Token Schemas

Pydantic models for OTP and device trust management.
Handles one-time passwords and device trust operations.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class OTPType(str, Enum):
    """OTP type enumeration."""
    REGISTRATION = "registration"
    LOGIN = "login"
    PASSWORD_RESET = "password_reset"
    EMAIL_VERIFICATION = "email_verification"
    TWO_FACTOR = "two_factor"


class OTPCreate(BaseModel):
    """Schema for creating an OTP."""
    
    user_id: int = Field(..., description="User ID")
    otp_type: OTPType = Field(..., description="Type of OTP")
    expires_in_minutes: int = Field(default=15, ge=1, le=60, description="OTP expiration in minutes")
    max_attempts: int = Field(default=3, ge=1, le=10, description="Maximum verification attempts")
    ip_address: Optional[str] = Field(None, max_length=45, description="Client IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="Client user agent")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "otp_type": "email_verification",
                "expires_in_minutes": 15,
                "max_attempts": 3,
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        }


class OTPVerify(BaseModel):
    """Schema for OTP verification."""
    
    code: str = Field(..., min_length=6, max_length=6, description="OTP code")
    otp_type: OTPType = Field(..., description="Type of OTP")
    ip_address: Optional[str] = Field(None, max_length=45, description="Client IP address")
    user_agent: Optional[str] = Field(None, max_length=500, description="Client user agent")
    
    @validator('code')
    def validate_code(cls, v):
        """Validate OTP code format."""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "code": "123456",
                "otp_type": "email_verification",
                "ip_address": "192.168.1.1",
                "user_agent": "Mozilla/5.0..."
            }
        }


class OTPResponse(BaseModel):
    """Schema for OTP response data."""
    
    id: int = Field(..., description="OTP ID")
    user_id: int = Field(..., description="User ID")
    otp_type: str = Field(..., description="OTP type")
    is_used: bool = Field(..., description="Whether OTP has been used")
    attempts: int = Field(..., description="Number of verification attempts")
    max_attempts: int = Field(..., description="Maximum allowed attempts")
    attempts_remaining: int = Field(..., description="Remaining attempts")
    created_at: datetime = Field(..., description="OTP creation timestamp")
    expires_at: datetime = Field(..., description="OTP expiration timestamp")
    used_at: Optional[datetime] = Field(None, description="OTP usage timestamp")
    is_expired: bool = Field(..., description="Whether OTP is expired")
    is_valid: bool = Field(..., description="Whether OTP is valid for use")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "otp_type": "email_verification",
                "is_used": False,
                "attempts": 0,
                "max_attempts": 3,
                "attempts_remaining": 3,
                "created_at": "2023-01-01T12:00:00Z",
                "expires_at": "2023-01-01T12:15:00Z",
                "used_at": None,
                "is_expired": False,
                "is_valid": True
            }
        }


class DeviceTrustCreate(BaseModel):
    """Schema for creating device trust."""
    
    user_id: int = Field(..., description="User ID")
    device_name: Optional[str] = Field(None, max_length=255, description="Device name")
    user_agent: Optional[str] = Field(None, max_length=500, description="User agent string")
    ip_address: Optional[str] = Field(None, max_length=45, description="IP address")
    browser: Optional[str] = Field(None, max_length=100, description="Browser name")
    os: Optional[str] = Field(None, max_length=100, description="Operating system")
    expires_in_days: int = Field(default=30, ge=1, le=365, description="Trust expiration in days")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "device_name": "John's MacBook Pro",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
                "ip_address": "192.168.1.100",
                "browser": "Chrome",
                "os": "macOS",
                "expires_in_days": 30
            }
        }


class DeviceTrustResponse(BaseModel):
    """Schema for device trust response data."""
    
    id: int = Field(..., description="Device trust ID")
    user_id: int = Field(..., description="User ID")
    device_token: str = Field(..., description="Device trust token")
    device_name: Optional[str] = Field(None, description="Device name")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="IP address")
    browser: Optional[str] = Field(None, description="Browser name")
    os: Optional[str] = Field(None, description="Operating system")
    is_active: bool = Field(..., description="Whether device trust is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_used_at: datetime = Field(..., description="Last usage timestamp")
    expires_at: datetime = Field(..., description="Expiration timestamp")
    is_expired: bool = Field(..., description="Whether device trust is expired")
    is_valid: bool = Field(..., description="Whether device trust is valid")
    days_until_expiry: int = Field(..., description="Days until expiration")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "device_token": "dt_abc123xyz789",
                "device_name": "John's MacBook Pro",
                "user_agent": "Mozilla/5.0...",
                "ip_address": "192.168.1.100",
                "browser": "Chrome",
                "os": "macOS",
                "is_active": True,
                "created_at": "2023-01-01T12:00:00Z",
                "last_used_at": "2023-01-01T12:00:00Z",
                "expires_at": "2023-01-31T12:00:00Z",
                "is_expired": False,
                "is_valid": True,
                "days_until_expiry": 30
            }
        }


class DeviceTrustList(BaseModel):
    """Schema for device trust list."""
    
    devices: List[DeviceTrustResponse] = Field(..., description="List of trusted devices")
    total: int = Field(..., description="Total number of trusted devices")
    active_count: int = Field(..., description="Number of active trusted devices")
    
    class Config:
        schema_extra = {
            "example": {
                "devices": [
                    {
                        "id": 1,
                        "device_name": "John's MacBook Pro",
                        "browser": "Chrome",
                        "os": "macOS",
                        "is_active": True,
                        "last_used_at": "2023-01-01T12:00:00Z",
                        "expires_at": "2023-01-31T12:00:00Z"
                    }
                ],
                "total": 3,
                "active_count": 2
            }
        }


class DeviceTrustUpdate(BaseModel):
    """Schema for updating device trust."""
    
    device_name: Optional[str] = Field(None, max_length=255, description="Device name")
    is_active: Optional[bool] = Field(None, description="Device trust status")
    extend_days: Optional[int] = Field(None, ge=1, le=365, description="Days to extend expiration")
    
    class Config:
        schema_extra = {
            "example": {
                "device_name": "Updated Device Name",
                "is_active": True,
                "extend_days": 30
            }
        }