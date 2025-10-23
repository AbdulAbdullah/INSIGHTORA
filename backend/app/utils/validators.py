"""
Pydantic validators for input validation (Updated for Pydantic v2)
"""

from pydantic import BaseModel, field_validator, Field, model_validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

from app.models.data_source import DataSourceType
from app.models.query import QueryType
from app.models.dashboard import WidgetType


class UserCreate(BaseModel):
    """Validation model for user creation"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    name: str = Field(..., min_length=2, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    account_type: str = Field(default="Individual", pattern=r'^(Individual|Business)$')
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
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=1)
    remember_me: bool = Field(default=False)
    device_name: Optional[str] = Field(None, max_length=255)


class DataSourceCreate(BaseModel):
    """Validation model for data source creation"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    type: DataSourceType
    connection_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_connection_config(self):
        if self.type in [DataSourceType.POSTGRESQL, DataSourceType.MYSQL, DataSourceType.SQLSERVER]:
            required_fields = ['host', 'port', 'database', 'username', 'password']
            for field in required_fields:
                if field not in self.connection_config:
                    raise ValueError(f'Missing required field for {self.type.value}: {field}')
        return self


class QueryCreate(BaseModel):
    """Validation model for query creation"""
    data_source_id: Optional[int] = None
    natural_language: Optional[str] = Field(None, max_length=1000)
    sql_query: Optional[str] = Field(None, max_length=5000)
    query_type: QueryType = QueryType.NATURAL_LANGUAGE
    
    @model_validator(mode='after')
    def validate_query_content(self):
        if not self.natural_language and not self.sql_query:
            raise ValueError('Either natural_language or sql_query must be provided')
        return self


class DashboardCreate(BaseModel):
    """Validation model for dashboard creation"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    layout_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    theme: Optional[str] = Field(default="light", max_length=50)
    is_public: bool = Field(default=False)
    tags: Optional[List[str]] = Field(default_factory=list)
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v


class WidgetCreate(BaseModel):
    """Validation model for widget creation"""
    dashboard_id: int
    title: str = Field(..., min_length=1, max_length=255)
    widget_type: WidgetType
    position: Dict[str, Any] = Field(..., description="Position and size config")
    data_config: Dict[str, Any] = Field(..., description="Data source and query config")
    style_config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class FileUploadParams(BaseModel):
    """Validation model for file upload parameters"""
    content_type: str
    size: int
    
    @field_validator('content_type')
    @classmethod
    def validate_content_type(cls, v):
        allowed_types = [
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/json'
        ]
        if v not in allowed_types:
            raise ValueError(f'Content type {v} not allowed')
        return v
    
    @field_validator('size')
    @classmethod
    def validate_size(cls, v):
        max_size = 100 * 1024 * 1024  # 100MB
        if v > max_size:
            raise ValueError('File size exceeds maximum limit of 100MB')
        return v


class PaginationParams(BaseModel):
    """Validation model for pagination parameters"""
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)
    sort_by: Optional[str] = Field(None, max_length=50)
    sort_order: Optional[str] = Field(default="asc", pattern=r'^(asc|desc)$')


class DateRangeFilter(BaseModel):
    """Validation model for date range filtering"""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    
    @model_validator(mode='after')
    def validate_date_range(self):
        if self.date_from and self.date_to and self.date_from >= self.date_to:
            raise ValueError('date_from must be before date_to')
        return self


class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None