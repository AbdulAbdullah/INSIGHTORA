"""
User Schemas

Pydantic models for user management including profile, settings,
permissions, and administrative operations.
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from app.shared.constants import UserRole


class UserCreate(BaseModel):
    """Schema for creating a new user (admin operation)."""
    
    email: EmailStr = Field(..., description="User email address")
    full_name: str = Field(..., min_length=2, max_length=255, description="User full name")
    password: str = Field(..., min_length=8, max_length=128, description="User password")
    role: str = Field(default=UserRole.USER.value, description="User role")
    is_active: bool = Field(default=True, description="User active status")
    email_verified: bool = Field(default=False, description="Email verification status")
    timezone: Optional[str] = Field(default="UTC", max_length=50, description="User timezone")
    language: Optional[str] = Field(default="en", max_length=10, description="User language")
    permissions: Optional[List[str]] = Field(default=[], description="User permissions")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate user role."""
        valid_roles = [role.value for role in UserRole]
        if v not in valid_roles:
            raise ValueError(f'Role must be one of: {valid_roles}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "email": "admin@example.com",
                "full_name": "Admin User",
                "password": "securepassword123",
                "role": "admin",
                "is_active": True,
                "email_verified": True,
                "timezone": "UTC",
                "language": "en",
                "permissions": ["users.read", "users.write"]
            }
        }


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    
    full_name: Optional[str] = Field(None, min_length=2, max_length=255, description="User full name")
    role: Optional[str] = Field(None, description="User role")
    is_active: Optional[bool] = Field(None, description="User active status")
    email_verified: Optional[bool] = Field(None, description="Email verification status")
    timezone: Optional[str] = Field(None, max_length=50, description="User timezone")
    language: Optional[str] = Field(None, max_length=10, description="User language")
    avatar_url: Optional[str] = Field(None, max_length=500, description="User avatar URL")
    two_factor_enabled: Optional[bool] = Field(None, description="Two-factor authentication status")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate user role."""
        if v is not None:
            valid_roles = [role.value for role in UserRole]
            if v not in valid_roles:
                raise ValueError(f'Role must be one of: {valid_roles}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "full_name": "Updated Name",
                "timezone": "America/New_York",
                "language": "es",
                "two_factor_enabled": True
            }
        }


class UserResponse(BaseModel):
    """Schema for user response data."""
    
    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: str = Field(..., description="User role")
    is_active: bool = Field(..., description="User active status")
    email_verified: bool = Field(..., description="Email verification status")
    email_verified_at: Optional[datetime] = Field(None, description="Email verification timestamp")
    timezone: str = Field(..., description="User timezone")
    language: str = Field(..., description="User language")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    two_factor_enabled: bool = Field(..., description="Two-factor authentication status")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    last_login_at: Optional[datetime] = Field(None, description="Last login timestamp")
    password_changed_at: datetime = Field(..., description="Password change timestamp")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "email_verified": True,
                "email_verified_at": "2023-01-01T12:00:00Z",
                "timezone": "UTC",
                "language": "en",
                "avatar_url": "https://example.com/avatar.jpg",
                "two_factor_enabled": False,
                "created_at": "2023-01-01T10:00:00Z",
                "updated_at": "2023-01-01T12:00:00Z",
                "last_login_at": "2023-01-01T11:30:00Z",
                "password_changed_at": "2023-01-01T10:00:00Z"
            }
        }


class UserProfile(BaseModel):
    """Schema for user profile information (public view)."""
    
    id: int = Field(..., description="User ID")
    full_name: str = Field(..., description="User full name")
    avatar_url: Optional[str] = Field(None, description="User avatar URL")
    timezone: str = Field(..., description="User timezone")
    language: str = Field(..., description="User language")
    created_at: datetime = Field(..., description="Account creation timestamp")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": 1,
                "full_name": "John Doe",
                "avatar_url": "https://example.com/avatar.jpg",
                "timezone": "UTC",
                "language": "en",
                "created_at": "2023-01-01T10:00:00Z"
            }
        }


class UserSettings(BaseModel):
    """Schema for user settings update."""
    
    timezone: Optional[str] = Field(None, max_length=50, description="User timezone")
    language: Optional[str] = Field(None, max_length=10, description="User language")
    avatar_url: Optional[str] = Field(None, max_length=500, description="User avatar URL")
    
    class Config:
        schema_extra = {
            "example": {
                "timezone": "America/New_York",
                "language": "es",
                "avatar_url": "https://example.com/new-avatar.jpg"
            }
        }


class UserPermissions(BaseModel):
    """Schema for user permissions management."""
    
    permissions: List[str] = Field(..., description="List of user permissions")
    
    class Config:
        schema_extra = {
            "example": {
                "permissions": [
                    "users.read",
                    "users.write",
                    "data_sources.read",
                    "data_sources.write"
                ]
            }
        }


class UserList(BaseModel):
    """Schema for paginated user list."""
    
    users: List[UserResponse] = Field(..., description="List of users")
    total: int = Field(..., description="Total number of users")
    page: int = Field(..., description="Current page number")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
    
    class Config:
        schema_extra = {
            "example": {
                "users": [
                    {
                        "id": 1,
                        "email": "user1@example.com",
                        "full_name": "User One",
                        "role": "user",
                        "is_active": True,
                        "email_verified": True,
                        "created_at": "2023-01-01T10:00:00Z"
                    }
                ],
                "total": 50,
                "page": 1,
                "per_page": 10,
                "pages": 5
            }
        }


class UserSearch(BaseModel):
    """Schema for user search parameters."""
    
    query: Optional[str] = Field(None, max_length=255, description="Search query")
    role: Optional[str] = Field(None, description="Filter by role")
    is_active: Optional[bool] = Field(None, description="Filter by active status")
    email_verified: Optional[bool] = Field(None, description="Filter by email verification")
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=10, ge=1, le=100, description="Items per page")
    
    @validator('role')
    def validate_role(cls, v):
        """Validate role filter."""
        if v is not None:
            valid_roles = [role.value for role in UserRole]
            if v not in valid_roles:
                raise ValueError(f'Role must be one of: {valid_roles}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "query": "john",
                "role": "user",
                "is_active": True,
                "email_verified": True,
                "page": 1,
                "per_page": 10
            }
        }