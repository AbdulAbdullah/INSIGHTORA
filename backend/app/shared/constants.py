"""
Application Constants

Centralized constants used across the application.
"""

from enum import Enum


MAX_FILE_SIZE_MB = 100
ALLOWED_FILE_EXTENSIONS = {
    "csv": ["csv", "txt"],
    "excel": ["xlsx", "xls"],
    "json": ["json"],
    "parquet": ["parquet"]
}

MIME_TYPE_MAPPING = {
    "text/csv": "csv",
    "application/csv": "csv",
    "text/plain": "csv",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "excel",
    "application/vnd.ms-excel": "excel",
    "application/json": "json",
    "text/json": "json",
    "application/octet-stream": "parquet"
}

SUPPORTED_DATABASES = [
    "postgresql",
    "mysql",
    "sqlite",
    "mssql",
    "oracle"
]

DEFAULT_CONNECTION_TIMEOUT = 30
DEFAULT_QUERY_TIMEOUT = 300
MAX_QUERY_RESULTS = 10000

OTP_LENGTH = 6
OTP_EXPIRY_MINUTES = 10
MAX_OTP_ATTEMPTS = 3
DEVICE_TRUST_DAYS = 30
PASSWORD_RESET_EXPIRY_HOURS = 24

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
API_VERSION = "v1"

SUPPORTED_CHART_TYPES = [
    "bar",
    "line",
    "pie",
    "doughnut",
    "area",
    "scatter",
    "bubble",
    "histogram",
    "box",
    "heatmap",
    "treemap",
    "sankey",
    "gantt",
    "geographic"
]

DEFAULT_CHART_COLORS = [
    "#3B82F6",
    "#EF4444",
    "#10B981",
    "#F59E0B",
    "#8B5CF6",
    "#F97316",
    "#06B6D4",
    "#84CC16",
    "#EC4899",
    "#6B7280"
]

SUPPORTED_AI_PROVIDERS = ["groq", "openai", "anthropic"]
DEFAULT_AI_MODEL = "llama-3.1-8b-instant"
MAX_CONTEXT_LENGTH = 4000
DEFAULT_TEMPERATURE = 0.1

CACHE_PREFIXES = {
    "user": "user:",
    "query": "query:",
    "chart": "chart:",
    "data": "data:",
    "session": "session:"
}

DEFAULT_CACHE_TTL = 3600
LONG_CACHE_TTL = 86400
SHORT_CACHE_TTL = 300

ERROR_MESSAGES = {
    "INVALID_CREDENTIALS": "Invalid email or password",
    "EMAIL_NOT_VERIFIED": "Please verify your email address",
    "ACCOUNT_DISABLED": "Your account has been disabled",
    "OTP_EXPIRED": "OTP has expired, please request a new one",
    "OTP_INVALID": "Invalid OTP code",
    "FILE_TOO_LARGE": "File size exceeds maximum allowed size",
    "UNSUPPORTED_FORMAT": "File format is not supported",
    "DATABASE_CONNECTION_FAILED": "Failed to connect to database",
    "QUERY_TIMEOUT": "Query execution timed out",
    "INSUFFICIENT_PERMISSIONS": "You don't have permission to perform this action",
    "RESOURCE_NOT_FOUND": "Requested resource was not found",
    "RATE_LIMIT_EXCEEDED": "Too many requests, please try again later"
}

SUCCESS_MESSAGES = {
    "USER_REGISTERED": "User registered successfully",
    "EMAIL_VERIFIED": "Email verified successfully",
    "LOGIN_SUCCESSFUL": "Login successful",
    "PASSWORD_RESET": "Password reset successfully",
    "FILE_UPLOADED": "File uploaded successfully",
    "DATA_SOURCE_CONNECTED": "Data source connected successfully",
    "QUERY_EXECUTED": "Query executed successfully",
    "CHART_GENERATED": "Chart generated successfully",
    "DASHBOARD_SAVED": "Dashboard saved successfully"
}


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"


class DataSourceType(str, Enum):
    """Data source type enumeration."""
    DATABASE = "database"
    FILE = "file"
    API = "api"
    STREAM = "stream"


class QueryStatus(str, Enum):
    """Query execution status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ChartType(str, Enum):
    """Chart type enumeration."""
    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    BUBBLE = "bubble"
    HISTOGRAM = "histogram"
    BOX = "box"
    HEATMAP = "heatmap"
    TREEMAP = "treemap"
    SANKEY = "sankey"
    GANTT = "gantt"
    GEOGRAPHIC = "geographic"


class NotificationType(str, Enum):
    """Notification type enumeration."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    IN_APP = "in_app"


class FileProcessingStatus(str, Enum):
    """File processing status enumeration."""
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"