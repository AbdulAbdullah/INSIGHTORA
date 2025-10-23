"""
User models for authentication and user management
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
    
    # Relationships
    data_sources = relationship("DataSource", back_populates="owner", cascade="all, delete-orphan")
    dashboards = relationship("Dashboard", back_populates="owner", cascade="all, delete-orphan")
    queries = relationship("QueryHistory", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    
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


class UserSession(Base):
    """
    User session model for tracking active sessions and device trust
    """
    __tablename__ = "user_sessions"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session information
    session_token = Column(String(255), unique=True, index=True, nullable=False)
    refresh_token = Column(String(255), unique=True, index=True, nullable=False)
    
    # Device information
    device_fingerprint = Column(String(255), nullable=True)
    device_name = Column(String(255), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    
    # Location information
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Trust and security
    is_trusted = Column(Boolean, default=False)
    trust_expires_at = Column(DateTime, nullable=True)
    
    # Session status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, device_name={self.device_name})>"


class UserOTP(Base):
    """
    OTP (One-Time Password) model for two-factor authentication
    """
    __tablename__ = "user_otps"
    
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
        return f"<UserOTP(id={self.id}, user_id={self.user_id}, type={self.otp_type})>"


class UserAPIKey(Base):
    """
    API key model for programmatic access
    """
    __tablename__ = "user_api_keys"
    
    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # API key information
    name = Column(String(255), nullable=False)
    key_prefix = Column(String(20), nullable=False)  # First few chars for display
    hashed_key = Column(String(255), nullable=False)
    
    # Permissions and scopes
    scopes = Column(JSON, default=list)  # List of allowed scopes
    
    # Usage tracking
    last_used = Column(DateTime, nullable=True)
    usage_count = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, name={self.name}, prefix={self.key_prefix})>"