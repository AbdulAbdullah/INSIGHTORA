"""
Data source models for database connections and file uploads
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.core.database import Base


class DataSourceType(PyEnum):
    """
    Enumeration of supported data source types
    """
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    SQLSERVER = "sqlserver"
    ORACLE = "oracle"
    MONGODB = "mongodb"
    SQLITE = "sqlite"
    CSV = "csv"
    EXCEL = "excel"
    JSON = "json"
    PARQUET = "parquet"
    API = "api"
    SNOWFLAKE = "snowflake"
    BIGQUERY = "bigquery"
    REDSHIFT = "redshift"


class DataSourceStatus(PyEnum):
    """
    Data source connection status
    """
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"
    PENDING = "pending"


class DataSource(Base):
    """
    Data source model for managing database connections and file uploads
    """
    __tablename__ = "data_sources"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Basic information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(Enum(DataSourceType), nullable=False)
    
    # Connection configuration (encrypted in production)
    connection_config = Column(JSON, default=dict)
    
    # File information (for file-based sources)
    file_path = Column(String(500), nullable=True)
    file_size = Column(Integer, nullable=True)  # in bytes
    file_mime_type = Column(String(100), nullable=True)
    original_filename = Column(String(255), nullable=True)
    
    # Schema and metadata
    schema_cache = Column(JSON, default=dict)  # Cached table/column information
    sample_data = Column(JSON, default=dict)   # Sample data for preview
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    
    # Connection health and monitoring
    status = Column(Enum(DataSourceStatus), default=DataSourceStatus.PENDING)
    last_tested = Column(DateTime, nullable=True)
    last_successful_connection = Column(DateTime, nullable=True)
    connection_error = Column(Text, nullable=True)
    
    # Performance metrics
    avg_query_time = Column(Integer, nullable=True)  # in milliseconds
    total_queries = Column(Integer, default=0)
    last_query_time = Column(DateTime, nullable=True)
    
    # Data quality metrics
    data_quality_score = Column(Integer, nullable=True)  # 0-100
    missing_values_count = Column(Integer, nullable=True)
    duplicate_rows_count = Column(Integer, nullable=True)
    
    # Settings and preferences
    auto_refresh = Column(Boolean, default=False)
    refresh_interval = Column(Integer, nullable=True)  # in minutes
    query_timeout = Column(Integer, default=30)  # in seconds
    
    # Security and access
    is_public = Column(Boolean, default=False)
    allowed_users = Column(JSON, default=list)  # List of user IDs with access
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="data_sources")
    queries = relationship("QueryHistory", back_populates="data_source", cascade="all, delete-orphan")
    tables = relationship("DataTable", back_populates="data_source", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataSource(id={self.id}, name={self.name}, type={self.type.value})>"
    
    def to_dict(self):
        """Convert data source to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "status": self.status.value,
            "file_path": self.file_path,
            "file_size": self.file_size,
            "file_mime_type": self.file_mime_type,
            "original_filename": self.original_filename,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "last_tested": self.last_tested.isoformat() if self.last_tested else None,
            "last_successful_connection": self.last_successful_connection.isoformat() if self.last_successful_connection else None,
            "data_quality_score": self.data_quality_score,
            "auto_refresh": self.auto_refresh,
            "refresh_interval": self.refresh_interval,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DataTable(Base):
    """
    Model for individual tables within a data source
    """
    __tablename__ = "data_tables"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    data_source_id = Column(Integer, ForeignKey("data_sources.id"), nullable=False)
    
    # Table information
    table_name = Column(String(255), nullable=False)
    schema_name = Column(String(255), nullable=True)
    table_type = Column(String(50), nullable=True)  # table, view, materialized_view
    
    # Metadata
    description = Column(Text, nullable=True)
    row_count = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    
    # Statistics
    last_analyzed = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    data_source = relationship("DataSource", back_populates="tables")
    columns = relationship("DataColumn", back_populates="table", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DataTable(id={self.id}, name={self.table_name}, schema={self.schema_name})>"


class DataColumn(Base):
    """
    Model for individual columns within a data table
    """
    __tablename__ = "data_columns"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    table_id = Column(Integer, ForeignKey("data_tables.id"), nullable=False)
    
    # Column information
    column_name = Column(String(255), nullable=False)
    data_type = Column(String(100), nullable=False)
    is_nullable = Column(Boolean, nullable=True)
    is_primary_key = Column(Boolean, default=False)
    is_foreign_key = Column(Boolean, default=False)
    
    # Constraints and defaults
    default_value = Column(Text, nullable=True)
    max_length = Column(Integer, nullable=True)
    precision = Column(Integer, nullable=True)
    scale = Column(Integer, nullable=True)
    
    # Statistics
    unique_count = Column(Integer, nullable=True)
    null_count = Column(Integer, nullable=True)
    min_value = Column(String(255), nullable=True)
    max_value = Column(String(255), nullable=True)
    avg_value = Column(String(255), nullable=True)
    
    # Sample values for reference
    sample_values = Column(JSON, default=list)
    
    # Metadata
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    table = relationship("DataTable", back_populates="columns")
    
    def __repr__(self):
        return f"<DataColumn(id={self.id}, name={self.column_name}, type={self.data_type})>"
    
    def to_dict(self):
        """Convert column to dictionary"""
        return {
            "id": self.id,
            "column_name": self.column_name,
            "data_type": self.data_type,
            "is_nullable": self.is_nullable,
            "is_primary_key": self.is_primary_key,
            "is_foreign_key": self.is_foreign_key,
            "default_value": self.default_value,
            "max_length": self.max_length,
            "unique_count": self.unique_count,
            "null_count": self.null_count,
            "sample_values": self.sample_values,
            "description": self.description,
        }