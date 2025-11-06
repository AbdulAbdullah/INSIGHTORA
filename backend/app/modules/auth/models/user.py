"""
User Model

Core user model for authentication and authorization.
Handles user data, roles, permissions, and profile information.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List
import json

from app.core.database import Base
from app.shared.constants import UserRole


class User(Base):
    """
    User model for authentication and authorization.
    
    Handles:
    - Basic user information (email, name, password)
    - Role-based access control
    - Permission management
    - Profile settings (timezone, language, avatar)
    - Security settings (2FA, password history)
    - Audit timestamps
    """
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    email_verified_at = Column(DateTime, nullable=True)
    
    role = Column(String(50), default=UserRole.USER.value)
    permissions = Column(Text, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    
    avatar_url = Column(String(500), nullable=True)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    two_factor_enabled = Column(Boolean, default=False)
    password_changed_at = Column(DateTime, server_default=func.now())
    
    otps = relationship("OTP", back_populates="user", cascade="all, delete-orphan")
    device_trusts = relationship("DeviceTrust", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        """String representation of user."""
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN.value
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if user has specific permission.
        
        Args:
            permission: Permission string to check
            
        Returns:
            bool: True if user has permission
        """
        if self.is_admin:
            return True
        
        if not self.permissions:
            return False
        
        try:
            user_permissions = json.loads(self.permissions)
            return permission in user_permissions
        except (json.JSONDecodeError, TypeError):
            return False
    
    def add_permission(self, permission: str) -> None:
        """
        Add permission to user.
        
        Args:
            permission: Permission string to add
        """
        try:
            permissions = json.loads(self.permissions) if self.permissions else []
        except (json.JSONDecodeError, TypeError):
            permissions = []
        
        if permission not in permissions:
            permissions.append(permission)
            self.permissions = json.dumps(permissions)
    
    def remove_permission(self, permission: str) -> None:
        """
        Remove permission from user.
        
        Args:
            permission: Permission string to remove
        """
        try:
            permissions = json.loads(self.permissions) if self.permissions else []
        except (json.JSONDecodeError, TypeError):
            return
        
        if permission in permissions:
            permissions.remove(permission)
            self.permissions = json.dumps(permissions)
    
    def get_permissions(self) -> List[str]:
        """
        Get list of user permissions.
        
        Returns:
            List[str]: List of permission strings
        """
        if not self.permissions:
            return []
        
        try:
            return json.loads(self.permissions)
        except (json.JSONDecodeError, TypeError):
            return []
    
    def update_last_login(self) -> None:
        """Update last login timestamp."""
        self.last_login_at = datetime.utcnow()
    
    def verify_email(self) -> None:
        """Mark email as verified."""
        self.email_verified = True
        self.email_verified_at = datetime.utcnow()
    
    def enable_two_factor(self) -> None:
        """Enable two-factor authentication."""
        self.two_factor_enabled = True
    
    def disable_two_factor(self) -> None:
        """Disable two-factor authentication."""
        self.two_factor_enabled = False
    
    def update_password_timestamp(self) -> None:
        """Update password changed timestamp."""
        self.password_changed_at = datetime.utcnow()