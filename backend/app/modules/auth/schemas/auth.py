"""
Authentication Schemas

Pydantic models for authentication flows including login, registration,
password management, and email verification.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, Any
from datetime import datetime


class LoginRequest(BaseModel):
    """Request schema for user login."""
    
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    remember_device: bool = Field(default=False, description="Remember this device for future logins")
    otp_code: Optional[str] = Field(None, min_length=6, max_length=6, description="Two-factor authentication code")
    device_name: Optional[str] = Field(None, max_length=255, description="Name for this device")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "securepassword123",
                "remember_device": True,
                "device_name": "My Laptop"
            }
        }


class LoginResponse(BaseModel):
    """Response schema for successful login."""
    
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: Dict[str, Any] = Field(..., description="User information")
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    device_trusted: bool = Field(default=False, description="Whether device is trusted")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "full_name": "John Doe",
                    "role": "user"
                },
                "requires_2fa": False,
                "device_trusted": True
            }
        }


class RegisterRequest(BaseModel):
    """Request schema for user registration."""
    
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="User full name")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="Password confirmation")
    timezone: Optional[str] = Field(default="UTC", max_length=50, description="User timezone")
    language: Optional[str] = Field(default="en", max_length=10, description="User language preference")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate that passwords match."""
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('full_name')
    def validate_full_name(cls, v):
        """Validate full name format."""
        if not v.strip():
            raise ValueError('Full name cannot be empty')
        if len(v.strip()) < 2:
            raise ValueError('Full name must be at least 2 characters')
        return v.strip()
    
    class Config:
        schema_extra = {
            "example": {
                "email": "newuser@example.com",
                "full_name": "Jane Smith",
                "password": "securepassword123",
                "confirm_password": "securepassword123",
                "timezone": "America/New_York",
                "language": "en"
            }
        }


class RegisterResponse(BaseModel):
    """Response schema for successful registration."""
    
    message: str = Field(..., description="Success message")
    user_id: int = Field(..., description="Created user ID")
    email_verification_required: bool = Field(default=True, description="Whether email verification is required")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Registration successful. Please check your email for verification.",
                "user_id": 123,
                "email_verification_required": True
            }
        }


class PasswordResetRequest(BaseModel):
    """Request schema for password reset initiation."""
    
    email: EmailStr = Field(..., description="User email address")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class PasswordResetResponse(BaseModel):
    """Response schema for password reset initiation."""
    
    message: str = Field(..., description="Success message")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "If an account with this email exists, you will receive a password reset link."
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request schema for password change."""
    
    current_password: str = Field(..., min_length=8, max_length=128, description="Current password")
    new_password: str = Field(..., min_length=8, max_length=128, description="New password")
    confirm_password: str = Field(..., min_length=8, max_length=128, description="New password confirmation")
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        """Validate that new passwords match."""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v
    
    @validator('new_password')
    def validate_new_password(cls, v, values, **kwargs):
        """Validate new password is different from current."""
        if 'current_password' in values and v == values['current_password']:
            raise ValueError('New password must be different from current password')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "current_password": "oldpassword123",
                "new_password": "newsecurepassword456",
                "confirm_password": "newsecurepassword456"
            }
        }


class VerifyEmailRequest(BaseModel):
    """Request schema for email verification."""
    
    email: EmailStr = Field(..., description="User email address")
    otp_code: str = Field(..., min_length=6, max_length=6, description="Email verification code")
    
    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "otp_code": "123456"
            }
        }


class VerifyEmailResponse(BaseModel):
    """Response schema for email verification."""
    
    message: str = Field(..., description="Success message")
    email_verified: bool = Field(..., description="Email verification status")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Email verified successfully",
                "email_verified": True
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""
    
    refresh_token: str = Field(..., description="JWT refresh token")
    
    class Config:
        schema_extra = {
            "example": {
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
            }
        }


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""
    
    access_token: str = Field(..., description="New JWT access token")
    refresh_token: str = Field(..., description="New JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        schema_extra = {
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600
            }
        }