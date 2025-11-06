"""
Custom Exception Hierarchy

Defines application-specific exceptions with proper error codes and messages.
"""

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class BaseAppException(Exception):
    """Base exception for all application exceptions."""
    
    def __init__(
        self,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(BaseAppException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={"field": field} if field else {}
        )


class AuthenticationException(BaseAppException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(BaseAppException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR"
        )


class ResourceNotFoundException(BaseAppException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class ResourceConflictException(BaseAppException):
    """Exception for resource conflict errors."""
    
    def __init__(self, resource: str, message: str):
        super().__init__(
            message=message,
            error_code="RESOURCE_CONFLICT",
            details={"resource": resource}
        )


class ExternalServiceException(BaseAppException):
    """Exception for external service errors."""
    
    def __init__(self, service: str, message: str):
        super().__init__(
            message=f"{service} service error: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={"service": service}
        )


class DataProcessingException(BaseAppException):
    """Exception for data processing errors."""
    
    def __init__(self, message: str, operation: Optional[str] = None):
        super().__init__(
            message=message,
            error_code="DATA_PROCESSING_ERROR",
            details={"operation": operation} if operation else {}
        )


class RateLimitException(BaseAppException):
    """Exception for rate limit errors."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED"
        )


def map_exception_to_http(exception: BaseAppException) -> HTTPException:
    """
    Map application exceptions to HTTP exceptions.
    
    Args:
        exception: Application exception
        
    Returns:
        HTTPException: Corresponding HTTP exception
    """
    status_code_map = {
        "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
        "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
        "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
        "RESOURCE_NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "RESOURCE_CONFLICT": status.HTTP_409_CONFLICT,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
        "DATA_PROCESSING_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
    }
    
    status_code = status_code_map.get(
        exception.error_code,
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    
    return HTTPException(
        status_code=status_code,
        detail={
            "error": exception.error_code,
            "message": exception.message,
            "details": exception.details
        }
    )
