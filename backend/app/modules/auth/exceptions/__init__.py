"""
Authentication Exceptions

Custom exception classes for the auth module.
Provides specific error handling for authentication and user management operations.
"""

from .auth import (
    AuthenticationException, InvalidCredentialsException, AccountLockedException,
    TwoFactorRequiredException, InvalidOTPException, OTPExpiredException,
    OTPAttemptsExceededException, DeviceNotTrustedException, TokenExpiredException,
    InvalidTokenException, RefreshTokenException
)
from .user import (
    UserException, UserNotFoundException, UserAlreadyExistsException,
    EmailNotVerifiedException, EmailAlreadyVerifiedException, InactiveUserException,
    PermissionDeniedException, InvalidRoleException, WeakPasswordException,
    PasswordMismatchException, SamePasswordException, ProfileUpdateException,
    AvatarUploadException, UserDeletionException, AdminRequiredException
)

__all__ = [
    "AuthenticationException", "InvalidCredentialsException", "AccountLockedException",
    "TwoFactorRequiredException", "InvalidOTPException", "OTPExpiredException",
    "OTPAttemptsExceededException", "DeviceNotTrustedException", "TokenExpiredException",
    "InvalidTokenException", "RefreshTokenException",
    
    "UserException", "UserNotFoundException", "UserAlreadyExistsException",
    "EmailNotVerifiedException", "EmailAlreadyVerifiedException", "InactiveUserException",
    "PermissionDeniedException", "InvalidRoleException", "WeakPasswordException",
    "PasswordMismatchException", "SamePasswordException", "ProfileUpdateException",
    "AvatarUploadException", "UserDeletionException", "AdminRequiredException"
]