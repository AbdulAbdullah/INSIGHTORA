"""
Authentication Dependencies

FastAPI dependency injection functions for authentication and authorization.
Provides reusable dependencies for route protection and user context.
"""

from .auth import (
    get_current_user, get_current_active_user, get_current_verified_user,
    get_optional_user, verify_token, require_auth, require_verified_email,
    require_two_factor, get_device_trust
)
from .permissions import (
    require_permission, require_role, require_admin, require_owner_or_admin,
    check_user_permission, check_user_role, get_user_permissions
)

__all__ = [
    "get_current_user", "get_current_active_user", "get_current_verified_user",
    "get_optional_user", "verify_token", "require_auth", "require_verified_email",
    "require_two_factor", "get_device_trust",
    
    "require_permission", "require_role", "require_admin", "require_owner_or_admin",
    "check_user_permission", "check_user_role", "get_user_permissions"
]