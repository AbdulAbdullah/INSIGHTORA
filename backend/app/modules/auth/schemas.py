"""
Auth Module Schemas - Pydantic models for request/response validation
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime
import re


# Request Schemas
class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="Valid email address")
    name: str = Field(..., min_length=2, max_length=100, description="Full name")
    password: str = Field(..., min_length=8, max_length=128, description="Password")
    account_type: Optional[str] = Field("Individual", description="Account type")
    company: Optional[str] = Field(None, max_length=255, description="Company name")
    job_title: Optional[str] = Field(None, max_length=255, description="Job title")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    
    @validator('password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v and not re.match(r'^\+?[\d\s\-\(\)]+$', v):
            raise ValueError('Invalid phone number format')
        return v


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr = Field(..., description="Email address")
    password: str = Field(..., description="Password")
    remember_device: Optional[bool] = Field(False, description="Remember this device")
    device_name: Optional[str] = Field(None, description="Device name for identification")


class OTPVerify(BaseModel):
    """Schema for OTP verification"""
    email: EmailStr = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    otp_type: str = Field(..., description="OTP type: registration, login, password_reset")
    remember_device: Optional[bool] = Field(False, description="Remember this device")
    device_name: Optional[str] = Field(None, description="Device name for identification")
    
    @validator('otp_code')
    def validate_otp_code(cls, v):
        """Validate OTP code format"""
        if not v.isdigit():
            raise ValueError('OTP code must contain only digits')
        if len(v) != 6:
            raise ValueError('OTP code must be exactly 6 digits')
        return v


class PasswordReset(BaseModel):
    """Schema for password reset request"""
    email: EmailStr = Field(..., description="Email address")


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    email: EmailStr = Field(..., description="Email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    
    @validator('new_password')
    def validate_password(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class DeviceTrustCreate(BaseModel):
    """Schema for creating device trust"""
    device_name: str = Field(..., max_length=255, description="Device name")
    device_type: Optional[str] = Field("desktop", description="Device type")
    trust_duration_days: Optional[int] = Field(30, ge=1, le=365, description="Trust duration in days")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str = Field(..., description="Refresh token")


# Response Schemas
class UserResponse(BaseModel):
    """Schema for user response (public data only)"""
    id: int
    email: str
    name: str
    is_active: bool
    is_verified: bool
    account_type: str
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    preferences: Dict[str, Any] = {}
    timezone: str = "UTC"
    language: str = "en"
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: UserResponse = Field(..., description="User information")


class OTPResponse(BaseModel):
    """Schema for OTP response"""
    message: str = Field(..., description="Response message")
    email_masked: str = Field(..., description="Masked email address")
    expires_in: int = Field(..., description="OTP expiration time in seconds")
    can_resend_after: Optional[int] = Field(None, description="Seconds until can resend OTP")


class DeviceTrustResponse(BaseModel):
    """Schema for device trust response"""
    id: int
    device_name: str
    device_type: Optional[str] = None
    trust_level: str
    trust_expires_at: datetime
    is_active: bool
    created_at: datetime
    last_used: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Schema for general auth response"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional response data")


# Utility Schemas
class PasswordStrengthCheck(BaseModel):
    """Schema for password strength check"""
    is_strong: bool
    score: int  # 0-100
    feedback: list[str]
    
    
class SecuritySettings(BaseModel):
    """Schema for user security settings"""
    two_factor_enabled: bool
    trusted_devices_count: int
    active_sessions_count: int
    last_password_change: Optional[datetime] = None
    login_notifications: bool = True
    
    class Config:
        from_attributes = True