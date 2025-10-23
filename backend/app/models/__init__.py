"""
Models initialization module
"""

# Import all models to ensure they're registered with SQLAlchemy
from .user import User, UserSession, UserOTP, UserAPIKey
from .data_source import DataSource, DataTable, DataColumn, DataSourceType, DataSourceStatus
from .query import QueryHistory, QueryVisualization, QueryCache, AIInsight, QueryStatus, QueryType
from .dashboard import (
    Dashboard, 
    DashboardWidget, 
    DashboardComment, 
    DashboardTemplate,
    DashboardStatus,
    WidgetType
)

# Export all models for easy importing
__all__ = [
    # User models
    "User",
    "UserSession", 
    "UserOTP",
    "UserAPIKey",
    
    # Data source models
    "DataSource",
    "DataTable",
    "DataColumn",
    "DataSourceType",
    "DataSourceStatus",
    
    # Query models
    "QueryHistory",
    "QueryVisualization",
    "QueryCache",
    "AIInsight",
    "QueryStatus",
    "QueryType",
    
    # Dashboard models
    "Dashboard",
    "DashboardWidget",
    "DashboardComment",
    "DashboardTemplate",
    "DashboardStatus",
    "WidgetType",
]