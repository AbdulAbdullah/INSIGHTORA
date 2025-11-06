"""
Authentication Module

Complete authentication system with user management, security, and access control.

Features:
- User registration and email verification
- Secure login with 2FA support
- Device trust management
- Role-based access control
- Permission management
- Password security and reset
- JWT token management
- Comprehensive audit logging

Architecture:
- Clean separation of concerns
- Repository pattern for data access
- Service layer for business logic
- Dependency injection for security
- RESTful API endpoints
"""

from .models import User, OTP, DeviceTrust

from .schemas import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse,
    PasswordResetRequest, PasswordResetResponse, ChangePasswordRequest,
    VerifyEmailRequest, VerifyEmailResponse, RefreshTokenRequest, RefreshTokenResponse,
    
    UserCreate, UserUpdate, UserResponse, UserProfile, UserSettings,
    UserPermissions, UserList, UserSearch,
    
    OTPCreate, OTPVerify, OTPResponse,
    DeviceTrustCreate, DeviceTrustResponse, DeviceTrustList
)

from .services import AuthService, TokenService, UserService

from .repositories import UserRepository, TokenRepository

from .dependencies import (
    get_current_user, get_current_active_user, get_current_verified_user,
    get_optional_user, verify_token, require_auth, require_verified_email,
    require_two_factor, get_device_trust,
    
    require_permission, require_role, require_admin, require_owner_or_admin,
    check_user_permission, check_user_role, get_user_permissions
)

from .exceptions import (
    AuthenticationException, InvalidCredentialsException, AccountLockedException,
    TwoFactorRequiredException, InvalidOTPException, OTPExpiredException,
    OTPAttemptsExceededException, DeviceNotTrustedException, TokenExpiredException,
    InvalidTokenException, RefreshTokenException,
    
    UserException, UserNotFoundException, UserAlreadyExistsException,
    EmailNotVerifiedException, EmailAlreadyVerifiedException, InactiveUserException,
    PermissionDeniedException, InvalidRoleException, WeakPasswordException,
    PasswordMismatchException, SamePasswordException
)

from .routes import router

__all__ = [
    "User", "OTP", "DeviceTrust",
    
    "LoginRequest", "LoginResponse", "RegisterRequest", "RegisterResponse",
    "PasswordResetRequest", "PasswordResetResponse", "ChangePasswordRequest",
    "VerifyEmailRequest", "VerifyEmailResponse", "RefreshTokenRequest", "RefreshTokenResponse",
    
    "UserCreate", "UserUpdate", "UserResponse", "UserProfile", "UserSettings",
    "UserPermissions", "UserList", "UserSearch",
    
    "OTPCreate", "OTPVerify", "OTPResponse",
    "DeviceTrustCreate", "DeviceTrustResponse", "DeviceTrustList",
    
    "AuthService", "TokenService", "UserService",
    
    "UserRepository", "TokenRepository",
    
    "get_current_user", "get_current_active_user", "get_current_verified_user",
    "get_optional_user", "verify_token", "require_auth", "require_verified_email",
    "require_two_factor", "get_device_trust",
    
    "require_permission", "require_role", "require_admin", "require_owner_or_admin",
    "check_user_permission", "check_user_role", "get_user_permissions",
    
    "AuthenticationException", "InvalidCredentialsException", "AccountLockedException",
    "TwoFactorRequiredException", "InvalidOTPException", "OTPExpiredException",
    "OTPAttemptsExceededException", "DeviceNotTrustedException", "TokenExpiredException",
    "InvalidTokenException", "RefreshTokenException",
    
    "UserException", "UserNotFoundException", "UserAlreadyExistsException",
    "EmailNotVerifiedException", "EmailAlreadyVerifiedException", "InactiveUserException",
    "PermissionDeniedException", "InvalidRoleException", "WeakPasswordException",
    "PasswordMismatchException", "SamePasswordException",
    
    "router"
]