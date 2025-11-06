"""
Authentication Models

Database models for the authentication module.
Clean separation of concerns with each model in its own file.
"""

from .user import User
from .token import OTP, DeviceTrust

__all__ = [
    "User",
    "OTP", 
    "DeviceTrust"
]