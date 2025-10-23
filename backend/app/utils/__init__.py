"""
Utilities module initialization
"""

from .exceptions import (
    SmartBIException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    DatabaseConnectionError,
    QueryExecutionError,
    DataProcessingError,
    FileProcessingError,
    AIServiceError,
    VisualizationError,
    BusinessLogicError,
)

from .data_processing import DataProcessor

from .validators import (
    UserCreate,
    UserLogin,
    DataSourceCreate,
    QueryCreate,
    DashboardCreate,
    WidgetCreate,
    FileUploadParams,
    PaginationParams,
    DateRangeFilter,
    APIResponse,
)

__all__ = [
    # Exceptions
    "SmartBIException",
    "AuthenticationError", 
    "AuthorizationError",
    "ValidationError",
    "DatabaseConnectionError",
    "QueryExecutionError",
    "DataProcessingError",
    "FileProcessingError",
    "AIServiceError",
    "VisualizationError",
    "BusinessLogicError",
    
    # Data processing
    "DataProcessor",
    
    # Validators
    "UserCreate",
    "UserLogin",
    "DataSourceCreate",
    "QueryCreate",
    "DashboardCreate",
    "WidgetCreate",
    "FileUpload",
    "PaginationParams",
    "FilterParams",
    "ChartConfig",
    "APIResponse",
    "ErrorResponse",
]