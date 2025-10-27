"""
Auth Module Exceptions - Custom exceptions for authentication
"""


class AuthenticationError(Exception):
    """Base authentication error"""
    def __init__(self, message: str = "Authentication failed"):
        self.message = message
        super().__init__(self.message)


class UserNotFoundError(AuthenticationError):
    """User not found error"""
    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class InvalidOTPError(AuthenticationError):
    """Invalid OTP error"""
    def __init__(self, message: str = "Invalid or expired OTP code"):
        super().__init__(message)


class AccountLockedError(AuthenticationError):
    """Account locked error"""
    def __init__(self, message: str = "Account is temporarily locked"):
        super().__init__(message)


class EmailNotVerifiedError(AuthenticationError):
    """Email not verified error"""
    def __init__(self, message: str = "Email address not verified"):
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """Invalid token error"""
    def __init__(self, message: str = "Invalid or expired token"):
        super().__init__(message)


class DeviceNotTrustedError(AuthenticationError):
    """Device not trusted error"""
    def __init__(self, message: str = "Device is not trusted"):
        super().__init__(message)


class PasswordTooWeakError(AuthenticationError):
    """Password too weak error"""
    def __init__(self, message: str = "Password does not meet security requirements"):
        super().__init__(message)


class RateLimitExceededError(AuthenticationError):
    """Rate limit exceeded error"""
    def __init__(self, message: str = "Too many requests. Please try again later."):
        super().__init__(message)