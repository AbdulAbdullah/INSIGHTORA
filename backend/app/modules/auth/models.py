"""
Auth Module Models - All authentication-related database models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    """
    User model for authentication and user management
    """
    __tablename__ = "users"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic user information
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Account type (Individual, Business)
    account_type = Column(String(50), default="Individual")
    
    # Profile information
    profile_picture = Column(String(500), nullable=True)
    company = Column(String(255), nullable=True)
    job_title = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Security settings
    two_factor_enabled = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Preferences and settings
    preferences = Column(JSON, default=dict)
    timezone = Column(String(50), default="UTC")
    language = Column(String(10), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)"""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "account_type": self.account_type,
            "company": self.company,
            "job_title": self.job_title,
            "phone": self.phone,
            "profile_picture": self.profile_picture,
            "preferences": self.preferences,
            "timezone": self.timezone,
            "language": self.language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
        }


class RefreshToken(Base):
    """
    Refresh token model for JWT token management
    """
    __tablename__ = "refresh_tokens"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Token information
    token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Device information
    device_fingerprint = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Trust and security
    is_trusted = Column(Boolean, default=False)
    trust_expires_at = Column(DateTime, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, device_name={self.device_name})>"


class OTPVerification(Base):
    """
    OTP (One-Time Password) model for two-factor authentication
    """
    __tablename__ = "otp_verifications"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # OTP information
    otp_code = Column(String(10), nullable=False)
    otp_type = Column(String(50), nullable=False)  # registration, login, password_reset
    
    # Security
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    # Status
    is_used = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    # Additional context
    context_data = Column(JSON, default=dict)  # Additional context like email, IP, etc.
    
    def __repr__(self):
        return f"<OTPVerification(id={self.id}, user_id={self.user_id}, type={self.otp_type})>"


class DeviceTrust(Base):
    """
    Device trust model for managing trusted devices
    """
    __tablename__ = "device_trusts"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Device identification
    device_fingerprint = Column(String(255), unique=True, index=True, nullable=False)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    
    # Device information
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    location = Column(String(255), nullable=True)
    
    # Trust settings
    trust_level = Column(String(50), default="basic")  # basic, high, administrative
    trust_expires_at = Column(DateTime, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DeviceTrust(id={self.id}, user_id={self.user_id}, device_name={self.device_name})>"