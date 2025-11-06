"""
Token Models

OTP and DeviceTrust models for authentication security.
Handles one-time passwords and device trust management.
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import Base


class OTP(Base):
    """
    One-Time Password model for email verification and 2FA.
    
    Handles:
    - Email verification codes
    - Password reset codes
    - Two-factor authentication codes
    - Attempt tracking and security
    """
    
    __tablename__ = "otps"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    code = Column(String(10), nullable=False)
    otp_type = Column(String(50), nullable=False)
    
    is_used = Column(Boolean, default=False)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    
    created_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="otps")
    
    def __repr__(self) -> str:
        """String representation of OTP."""
        return f"<OTP(id={self.id}, user_id={self.user_id}, type='{self.otp_type}', used={self.is_used})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if OTP is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """
        Check if OTP is valid for use.
        
        Returns:
            bool: True if OTP can be used (not used, not expired, attempts not exceeded)
        """
        return (
            not self.is_used and
            not self.is_expired and
            self.attempts < self.max_attempts
        )
    
    @property
    def attempts_remaining(self) -> int:
        """Get number of attempts remaining."""
        return max(0, self.max_attempts - self.attempts)
    
    def increment_attempts(self) -> None:
        """Increment attempt counter."""
        self.attempts += 1
    
    def mark_as_used(self) -> None:
        """Mark OTP as used."""
        self.is_used = True
        self.used_at = datetime.utcnow()
    
    def is_attempt_allowed(self) -> bool:
        """Check if another attempt is allowed."""
        return self.attempts < self.max_attempts


class DeviceTrust(Base):
    """
    Device trust model for "remember this device" functionality.
    
    Handles:
    - Device identification and tracking
    - Trust token management
    - Device information storage
    - Expiration and revocation
    """
    
    __tablename__ = "device_trusts"
    
    id = Column(Integer, primary_key=True, index=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    device_token = Column(String(255), unique=True, nullable=False)
    device_name = Column(String(255), nullable=True)
    
    user_agent = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    browser = Column(String(100), nullable=True)
    os = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, server_default=func.now())
    last_used_at = Column(DateTime, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    
    user = relationship("User", back_populates="device_trusts")
    
    def __repr__(self) -> str:
        """String representation of device trust."""
        return f"<DeviceTrust(id={self.id}, user_id={self.user_id}, device='{self.device_name}')>"
    
    @property
    def is_expired(self) -> bool:
        """Check if device trust is expired."""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """
        Check if device trust is valid.
        
        Returns:
            bool: True if device trust is active and not expired
        """
        return self.is_active and not self.is_expired
    
    @property
    def days_until_expiry(self) -> int:
        """Get number of days until expiry."""
        if self.is_expired:
            return 0
        
        delta = self.expires_at - datetime.utcnow()
        return max(0, delta.days)
    
    def update_last_used(self) -> None:
        """Update last used timestamp."""
        self.last_used_at = datetime.utcnow()
    
    def revoke(self) -> None:
        """Revoke device trust."""
        self.is_active = False
    
    def extend_expiry(self, days: int = 30) -> None:
        """
        Extend device trust expiry.
        
        Args:
            days: Number of days to extend (default: 30)
        """
        self.expires_at = datetime.utcnow() + timedelta(days=days)
    
    def is_same_device(self, user_agent: str, ip_address: str) -> bool:
        """
        Check if this represents the same device.
        
        Args:
            user_agent: User agent string to compare
            ip_address: IP address to compare
            
        Returns:
            bool: True if likely the same device
        """
        return (
            self.user_agent == user_agent and
            self.ip_address == ip_address
        )