"""
FastAPI Dependency Injection

Centralized dependencies for authentication, database, and common services.
"""

from typing import Optional, Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.core.database import get_async_session
from app.core.security import verify_token
from app.core.exceptions import AuthenticationException, map_exception_to_http
from app.modules.auth.repository import UserRepository

logger = logging.getLogger(__name__)

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Dependency to get current authenticated user.
    
    Args:
        credentials: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: Current authenticated user
        
    Raises:
        HTTPException: If authentication fails
    """
    if not credentials:
        raise map_exception_to_http(
            AuthenticationException("Missing authentication token")
        )
    
    try:
        payload = verify_token(credentials.credentials, "access")
        if not payload:
            raise AuthenticationException("Invalid or expired token")
        
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationException("Invalid token payload")
        
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(int(user_id))
        
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User account is disabled")
        
        return user
        
    except AuthenticationException as e:
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise map_exception_to_http(
            AuthenticationException("Authentication failed")
        )


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Dependency to get current active user.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        User: Current active user
    """
    if not current_user.is_active:
        raise map_exception_to_http(
            AuthenticationException("User account is disabled")
        )
    
    return current_user


async def get_current_verified_user(
    current_user = Depends(get_current_active_user)
):
    """
    Dependency to get current verified user.
    
    Args:
        current_user: Current user from get_current_active_user
        
    Returns:
        User: Current verified user
    """
    if not current_user.email_verified:
        raise map_exception_to_http(
            AuthenticationException("Email verification required")
        )
    
    return current_user


def require_permissions(*required_permissions: str):
    """
    Dependency factory for permission-based access control.
    
    Args:
        required_permissions: List of required permissions
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user = Depends(get_current_verified_user)
    ):
        """Check if user has required permissions."""
        user_permissions = set(current_user.permissions or [])
        
        if not all(perm in user_permissions for perm in required_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user
    
    return permission_checker


def require_roles(*required_roles: str):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_roles: List of required roles
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user = Depends(get_current_verified_user)
    ):
        """Check if user has required roles."""
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role privileges"
            )
        
        return current_user
    
    return role_checker


CommonDeps = {
    "db": Depends(get_async_session),
    "current_user": Depends(get_current_user),
    "active_user": Depends(get_current_active_user),
    "verified_user": Depends(get_current_verified_user),
}
