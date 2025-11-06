"""
Authentication Schemas

Pydantic models for request/response validation in the auth module.
Clean separation between auth flows, user management, and token handling.
"""

from .auth import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    PasswordResetRequest, PasswordResetResponse, ChangePasswordRequest,
    VerifyEmailRequest, VerifyEmailResponse, RefreshTokenRequest, RefreshTokenResponse
)
from .user import (
    UserCreate, UserUpdate, UserResponse, UserProfile, UserSettings,
    UserPermissions, UserList, UserSearch
)
from .token import (
    OTPCreate, OTPVerify, OTPResponse,
    DeviceTrustCreate, DeviceTrustResponse, DeviceTrustList
)

__all__ = [
    "LoginRequest", "LoginResponse", "RegisterRequest", "RegisterResponse",
    "PasswordResetRequest", "PasswordResetResponse", "ChangePasswordRequest",
    "VerifyEmailRequest", "VerifyEmailResponse", "RefreshTokenRequest", "RefreshTokenResponse",
    
    "UserCreate", "UserUpdate", "UserResponse", "UserProfile", "UserSettings",
    "UserPermissions", "UserList", "UserSearch",
    
    "OTPCreate", "OTPVerify", "OTPResponse",
    "DeviceTrustCreate", "DeviceTrustResponse", "DeviceTrustList"
]