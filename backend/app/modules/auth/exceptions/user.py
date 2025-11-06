"""
User Exceptions

Exception classes for user management operations including registration,
profile updates, permissions, and account management.
"""

from typing import Optional, Dict, Any, List


class UserException(Exception):
    """Base exception for user-related errors."""
    
    def __init__(
        self, 
        message: str = "User operation failed", 
        error_code: str = "USER_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class UserNotFoundException(UserException):
    """Exception raised when user is not found."""
    
    def __init__(
        self, 
        message: str = "User not found",
        user_identifier: Optional[str] = None
    ):
        details = {}
        if user_identifier:
            details["user_identifier"] = user_identifier
            
        super().__init__(
            message=message,
            error_code="USER_NOT_FOUND",
            details=details
        )


class UserAlreadyExistsException(UserException):
    """Exception raised when attempting to create a user that already exists."""
    
    def __init__(
        self, 
        message: str = "User already exists",
        email: Optional[str] = None
    ):
        details = {}
        if email:
            details["email"] = email
            
        super().__init__(
            message=message,
            error_code="USER_ALREADY_EXISTS",
            details=details
        )


class EmailNotVerifiedException(UserException):
    """Exception raised when email verification is required but not completed."""
    
    def __init__(
        self, 
        message: str = "Email verification required",
        email: Optional[str] = None
    ):
        details = {}
        if email:
            details["email"] = email
            
        super().__init__(
            message=message,
            error_code="EMAIL_NOT_VERIFIED",
            details=details
        )


class EmailAlreadyVerifiedException(UserException):
    """Exception raised when attempting to verify an already verified email."""
    
    def __init__(
        self, 
        message: str = "Email is already verified",
        email: Optional[str] = None
    ):
        details = {}
        if email:
            details["email"] = email
            
        super().__init__(
            message=message,
            error_code="EMAIL_ALREADY_VERIFIED",
            details=details
        )


class InactiveUserException(UserException):
    """Exception raised when attempting to authenticate an inactive user."""
    
    def __init__(
        self, 
        message: str = "User account is inactive",
        user_id: Optional[int] = None
    ):
        details = {}
        if user_id:
            details["user_id"] = user_id
            
        super().__init__(
            message=message,
            error_code="INACTIVE_USER",
            details=details
        )


class PermissionDeniedException(UserException):
    """Exception raised when user lacks required permissions."""
    
    def __init__(
        self, 
        message: str = "Permission denied",
        required_permission: Optional[str] = None,
        user_permissions: Optional[List[str]] = None
    ):
        details = {}
        if required_permission:
            details["required_permission"] = required_permission
        if user_permissions:
            details["user_permissions"] = user_permissions
            
        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            details=details
        )


class InvalidRoleException(UserException):
    """Exception raised when an invalid role is specified."""
    
    def __init__(
        self, 
        message: str = "Invalid user role",
        invalid_role: Optional[str] = None,
        valid_roles: Optional[List[str]] = None
    ):
        details = {}
        if invalid_role:
            details["invalid_role"] = invalid_role
        if valid_roles:
            details["valid_roles"] = valid_roles
            
        super().__init__(
            message=message,
            error_code="INVALID_ROLE",
            details=details
        )


class WeakPasswordException(UserException):
    """Exception raised when password doesn't meet security requirements."""
    
    def __init__(
        self, 
        message: str = "Password does not meet security requirements",
        requirements: Optional[List[str]] = None
    ):
        details = {}
        if requirements:
            details["requirements"] = requirements
            
        super().__init__(
            message=message,
            error_code="WEAK_PASSWORD",
            details=details
        )


class PasswordMismatchException(UserException):
    """Exception raised when password confirmation doesn't match."""
    
    def __init__(self, message: str = "Password confirmation does not match"):
        super().__init__(
            message=message,
            error_code="PASSWORD_MISMATCH"
        )


class SamePasswordException(UserException):
    """Exception raised when new password is the same as current password."""
    
    def __init__(self, message: str = "New password must be different from current password"):
        super().__init__(
            message=message,
            error_code="SAME_PASSWORD"
        )


class ProfileUpdateException(UserException):
    """Exception raised when user profile update fails."""
    
    def __init__(
        self, 
        message: str = "Failed to update user profile",
        field: Optional[str] = None,
        reason: Optional[str] = None
    ):
        details = {}
        if field:
            details["field"] = field
        if reason:
            details["reason"] = reason
            
        super().__init__(
            message=message,
            error_code="PROFILE_UPDATE_FAILED",
            details=details
        )


class AvatarUploadException(UserException):
    """Exception raised when avatar upload fails."""
    
    def __init__(
        self, 
        message: str = "Avatar upload failed",
        reason: Optional[str] = None,
        max_size_mb: Optional[int] = None
    ):
        details = {}
        if reason:
            details["reason"] = reason
        if max_size_mb:
            details["max_size_mb"] = max_size_mb
            
        super().__init__(
            message=message,
            error_code="AVATAR_UPLOAD_FAILED",
            details=details
        )


class UserDeletionException(UserException):
    """Exception raised when user deletion fails."""
    
    def __init__(
        self, 
        message: str = "Failed to delete user account",
        reason: Optional[str] = None
    ):
        details = {}
        if reason:
            details["reason"] = reason
            
        super().__init__(
            message=message,
            error_code="USER_DELETION_FAILED",
            details=details
        )


class AdminRequiredException(UserException):
    """Exception raised when admin privileges are required."""
    
    def __init__(
        self, 
        message: str = "Administrator privileges required",
        operation: Optional[str] = None
    ):
        details = {}
        if operation:
            details["operation"] = operation
            
        super().__init__(
            message=message,
            error_code="ADMIN_REQUIRED",
            details=details
        )