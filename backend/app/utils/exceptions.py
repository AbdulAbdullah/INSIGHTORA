"""
Custom exceptions for the Smart BI Platform
"""

from typing import Any, Dict, Optional


class SmartBIException(Exception):
    """
    Base exception class for Smart BI Platform
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary"""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details
        }


class AuthenticationError(SmartBIException):
    """
    Authentication related errors
    """
    pass


class AuthorizationError(SmartBIException):
    """
    Authorization related errors  
    """
    pass


class ValidationError(SmartBIException):
    """
    Data validation errors
    """
    pass


class DatabaseConnectionError(SmartBIException):
    """
    Database connection related errors
    """
    pass


class QueryExecutionError(SmartBIException):
    """
    SQL query execution errors
    """
    pass


class DataProcessingError(SmartBIException):
    """
    Data processing and transformation errors
    """
    pass


class FileProcessingError(SmartBIException):
    """
    File upload and processing errors
    """
    pass


class AIServiceError(SmartBIException):
    """
    AI/ML service related errors
    """
    pass


class VisualizationError(SmartBIException):
    """
    Chart and visualization generation errors
    """
    pass


class BusinessLogicError(SmartBIException):
    """
    Business logic validation errors
    """
    pass


class ConfigurationError(SmartBIException):
    """
    Configuration and settings errors
    """
    pass


class RateLimitError(SmartBIException):
    """
    Rate limiting errors
    """
    pass


class CacheError(SmartBIException):
    """
    Caching related errors
    """
    pass


class ExternalServiceError(SmartBIException):
    """
    External service integration errors
    """
    pass


# Specific error classes for common scenarios

class UserNotFoundError(AuthenticationError):
    """User not found in database"""
    def __init__(self, user_identifier: str):
        super().__init__(
            f"User not found: {user_identifier}",
            error_code="USER_NOT_FOUND",
            details={"user_identifier": user_identifier}
        )


class InvalidCredentialsError(AuthenticationError):
    """Invalid login credentials"""
    def __init__(self):
        super().__init__(
            "Invalid email or password",
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AuthenticationError):
    """JWT token has expired"""
    def __init__(self):
        super().__init__(
            "Authentication token has expired",
            error_code="TOKEN_EXPIRED"
        )


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions"""
    def __init__(self, required_permission: str):
        super().__init__(
            f"Insufficient permissions. Required: {required_permission}",
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_permission": required_permission}
        )


class DataSourceNotFoundError(BusinessLogicError):
    """Data source not found"""
    def __init__(self, data_source_id: int):
        super().__init__(
            f"Data source not found: {data_source_id}",
            error_code="DATA_SOURCE_NOT_FOUND",
            details={"data_source_id": data_source_id}
        )


class UnsupportedFileFormatError(FileProcessingError):
    """Unsupported file format"""
    def __init__(self, file_format: str, supported_formats: list):
        super().__init__(
            f"Unsupported file format: {file_format}. Supported formats: {', '.join(supported_formats)}",
            error_code="UNSUPPORTED_FILE_FORMAT",
            details={
                "file_format": file_format,
                "supported_formats": supported_formats
            }
        )


class FileTooLargeError(FileProcessingError):
    """File size exceeds limit"""
    def __init__(self, file_size: int, max_size: int):
        super().__init__(
            f"File size ({file_size} bytes) exceeds maximum allowed size ({max_size} bytes)",
            error_code="FILE_TOO_LARGE",
            details={
                "file_size": file_size,
                "max_size": max_size
            }
        )


class SQLGenerationError(AIServiceError):
    """Error generating SQL from natural language"""
    def __init__(self, natural_language_query: str, reason: str):
        super().__init__(
            f"Failed to generate SQL for query: '{natural_language_query}'. Reason: {reason}",
            error_code="SQL_GENERATION_FAILED",
            details={
                "natural_language_query": natural_language_query,
                "reason": reason
            }
        )


class ChartGenerationError(VisualizationError):
    """Error generating chart/visualization"""
    def __init__(self, chart_type: str, reason: str):
        super().__init__(
            f"Failed to generate {chart_type} chart. Reason: {reason}",
            error_code="CHART_GENERATION_FAILED",
            details={
                "chart_type": chart_type,
                "reason": reason
            }
        )


class InvalidQueryError(QueryExecutionError):
    """Invalid SQL query"""
    def __init__(self, query: str, error_message: str):
        super().__init__(
            f"Invalid SQL query: {error_message}",
            error_code="INVALID_QUERY",
            details={
                "query": query,
                "database_error": error_message
            }
        )