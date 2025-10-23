"""
Pydantic validators for input validation
"""

from pydantic import BaseModel, field_validator, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from app.models.data_source import DataSourceType
from app.models.query import QueryType
from app.models.dashboard import WidgetType


class UserCreate(BaseModel):
    """Validation model for user creation"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    account_type: str = Field(default="Individual", regex=r'^(Individual|Business)$')
    company: Optional[str] = Field(None, max_length=255)
    job_title: Optional[str] = Field(None, max_length=255)

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    """Validation model for user login"""
    email: str = Field(..., regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=1)
    remember_device: Optional[bool] = False


class DataSourceCreate(BaseModel):
    """Validation model for data source creation"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: DataSourceType
    connection_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('connection_config')
    def validate_connection_config(cls, v, values):
        data_source_type = values.get('type')
        
        if data_source_type in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL, DataSourceType.SQLSERVER]:
            required_fields = ['host', 'port', 'database', 'username', 'password']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'Missing required field for {data_source_type.value}: {field}')
        
        return v


class QueryCreate(BaseModel):
    """Validation model for query creation"""
    query_type: QueryType
    natural_language: Optional[str] = Field(None, max_length=2000)
    sql_query: Optional[str] = Field(None, max_length=10000)
    data_source_id: Optional[int] = None
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @field_validator('natural_language', 'sql_query')
    def validate_query_content(cls, v, values, field):
        query_type = values.get('query_type')
        
        if query_type == QueryType.NATURAL_LANGUAGE and field.name == 'natural_language':
            if not v or len(v.strip()) == 0:
                raise ValueError('Natural language query cannot be empty')
        
        if query_type == QueryType.SQL and field.name == 'sql_query':
            if not v or len(v.strip()) == 0:
                raise ValueError('SQL query cannot be empty')
        
        return v


class DashboardCreate(BaseModel):
    """Validation model for dashboard creation"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    layout_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    theme: Optional[str] = Field(default="default", max_length=50)
    is_public: Optional[bool] = False
    tags: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        for tag in v:
            if len(tag) > 50:
                raise ValueError('Tag length cannot exceed 50 characters')
        return v


class WidgetCreate(BaseModel):
    """Validation model for widget creation"""
    widget_type: WidgetType
    title: str = Field(..., min_length=1, max_length=255)
    subtitle: Optional[str] = Field(None, max_length=500)
    position_x: int = Field(default=0, ge=0)
    position_y: int = Field(default=0, ge=0)
    width: int = Field(default=4, ge=1, le=12)
    height: int = Field(default=3, ge=1, le=20)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    query_id: Optional[int] = None
    data_source_id: Optional[int] = None


class FileUpload(BaseModel):
    """Validation model for file upload"""
    filename: str = Field(..., min_length=1, max_length=255)
    content_type: str
    size: int = Field(..., gt=0)
    
    @field_validator('content_type')
    def validate_content_type(cls, v):
        allowed_types = [
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'application/json',
            'application/octet-stream'  # For parquet files
        ]
        if v not in allowed_types:
            raise ValueError(f'Unsupported file type: {v}')
        return v
    
    @field_validator('size')
    def validate_size(cls, v):
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError(f'File size ({v} bytes) exceeds maximum allowed size ({max_size} bytes)')
        return v


class PaginationParams(BaseModel):
    """Validation model for pagination parameters"""
    page: int = Field(default=1, ge=1)
    size: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[str] = Field(default="asc", regex=r'^(asc|desc)$')


class FilterParams(BaseModel):
    """Validation model for filtering parameters"""
    search: Optional[str] = Field(None, max_length=255)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    @field_validator('date_to')
    def validate_date_range(cls, v, values):
        date_from = values.get('date_from')
        if date_from and v and v < date_from:
            raise ValueError('date_to must be after date_from')
        return v


class ChartConfig(BaseModel):
    """Validation model for chart configuration"""
    chart_type: str = Field(..., min_length=1, max_length=50)
    title: Optional[str] = Field(None, max_length=255)
    x_axis: Optional[str] = Field(None, max_length=100)
    y_axis: Optional[str] = Field(None, max_length=100)
    color_scheme: Optional[str] = Field(default="default", max_length=50)
    width: Optional[int] = Field(default=800, ge=200, le=2000)
    height: Optional[int] = Field(default=400, ge=200, le=1200)
    config_options: Optional[Dict[str, Any]] = Field(default_factory=dict)


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)