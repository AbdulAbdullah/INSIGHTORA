"""
Auth Module - Authentication and Authorization

This module handles all authentication-related functionality:
- User registration and login
- OTP verification (email-based 2FA)
- JWT token management
- Device trust
- Password management
"""

from .models import User, OTPVerification, DeviceTrust, RefreshToken
from .schemas import (
    UserCreate, 
    UserLogin, 
    OTPVerify, 
    TokenResponse,
    UserResponse,
    DeviceTrustCreate
)
from .service import AuthService, OTPService
from .routes import router

__all__ = [
    # Models
    "User",
    "OTPVerification", 
    "DeviceTrust",
    "RefreshToken",
    
    # Schemas
    "UserCreate",
    "UserLogin", 
    "OTPVerify",
    "TokenResponse",
    "UserResponse",
    "DeviceTrustCreate",
    
    # Services
    "AuthService",
    "OTPService",
    
    # Router
    "router"
]