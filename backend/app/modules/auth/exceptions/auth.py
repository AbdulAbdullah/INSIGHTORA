"""
Authentication Exceptions

Exception classes for authentication-related errors including login,
token management, OTP verification, and device trust operations.
"""

from typing import Optional, Dict, Any


class AuthenticationException(Exception):
    """Base exception for authentication-related errors."""
    
    def __init__(
        self, 
        message: str = "Authentication failed", 
        error_code: str = "AUTH_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class InvalidCredentialsException(AuthenticationException):
    """Exception raised when login credentials are invalid."""
    
    def __init__(self, message: str = "Invalid email or password"):
        super().__init__(
            message=message,
            error_code="INVALID_CREDENTIALS"
        )


class AccountLockedException(AuthenticationException):
    """Exception raised when user account is locked due to failed attempts."""
    
    def __init__(
        self, 
        message: str = "Account temporarily locked due to failed login attempts",
        lockout_duration: Optional[int] = None
    ):
        details = {}
        if lockout_duration:
            details["lockout_duration_minutes"] = lockout_duration
            
        super().__init__(
            message=message,
            error_code="ACCOUNT_LOCKED",
            details=details
        )


class TwoFactorRequiredException(AuthenticationException):
    """Exception raised when two-factor authentication is required."""
    
    def __init__(
        self, 
        message: str = "Two-factor authentication required",
        otp_type: str = "login"
    ):
        super().__init__(
            message=message,
            error_code="TWO_FACTOR_REQUIRED",
            details={"otp_type": otp_type}
        )


class InvalidOTPException(AuthenticationException):
    """Exception raised when OTP code is invalid."""
    
    def __init__(
        self, 
        message: str = "Invalid verification code",
        attempts_remaining: Optional[int] = None
    ):
        details = {}
        if attempts_remaining is not None:
            details["attempts_remaining"] = attempts_remaining
            
        super().__init__(
            message=message,
            error_code="INVALID_OTP",
            details=details
        )


class OTPExpiredException(AuthenticationException):
    """Exception raised when OTP code has expired."""
    
    def __init__(self, message: str = "Verification code has expired"):
        super().__init__(
            message=message,
            error_code="OTP_EXPIRED"
        )


class OTPAttemptsExceededException(AuthenticationException):
    """Exception raised when OTP verification attempts are exceeded."""
    
    def __init__(
        self, 
        message: str = "Maximum verification attempts exceeded",
        max_attempts: int = 3
    ):
        super().__init__(
            message=message,
            error_code="OTP_ATTEMPTS_EXCEEDED",
            details={"max_attempts": max_attempts}
        )


class DeviceNotTrustedException(AuthenticationException):
    """Exception raised when device is not trusted and requires verification."""
    
    def __init__(
        self, 
        message: str = "Device not trusted, additional verification required",
        verification_method: str = "otp"
    ):
        super().__init__(
            message=message,
            error_code="DEVICE_NOT_TRUSTED",
            details={"verification_method": verification_method}
        )


class TokenExpiredException(AuthenticationException):
    """Exception raised when JWT token has expired."""
    
    def __init__(
        self, 
        message: str = "Token has expired",
        token_type: str = "access"
    ):
        super().__init__(
            message=message,
            error_code="TOKEN_EXPIRED",
            details={"token_type": token_type}
        )


class InvalidTokenException(AuthenticationException):
    """Exception raised when JWT token is invalid or malformed."""
    
    def __init__(
        self, 
        message: str = "Invalid token",
        token_type: str = "access"
    ):
        super().__init__(
            message=message,
            error_code="INVALID_TOKEN",
            details={"token_type": token_type}
        )


class RefreshTokenException(AuthenticationException):
    """Exception raised when refresh token operation fails."""
    
    def __init__(
        self, 
        message: str = "Failed to refresh token",
        reason: Optional[str] = None
    ):
        details = {}
        if reason:
            details["reason"] = reason
            
        super().__init__(
            message=message,
            error_code="REFRESH_TOKEN_FAILED",
            details=details
        )


class SessionExpiredException(AuthenticationException):
    """Exception raised when user session has expired."""
    
    def __init__(self, message: str = "Session has expired, please login again"):
        super().__init__(
            message=message,
            error_code="SESSION_EXPIRED"
        )


class ConcurrentLoginException(AuthenticationException):
    """Exception raised when concurrent login limit is exceeded."""
    
    def __init__(
        self, 
        message: str = "Maximum concurrent sessions exceeded",
        max_sessions: int = 5
    ):
        super().__init__(
            message=message,
            error_code="CONCURRENT_LOGIN_LIMIT",
            details={"max_sessions": max_sessions}
        )


class RateLimitExceededException(AuthenticationException):
    """Exception raised when rate limit for authentication attempts is exceeded."""
    
    def __init__(
        self, 
        message: str = "Too many authentication attempts, please try again later",
        retry_after: Optional[int] = None
    ):
        details = {}
        if retry_after:
            details["retry_after_seconds"] = retry_after
            
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            details=details
        )