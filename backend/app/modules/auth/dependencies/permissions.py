"""
Permission Dependencies

FastAPI dependencies for role-based and permission-based access control.
Provides flexible authorization mechanisms for route protection.
"""

from fastapi import Depends, HTTPException, status
from typing import List, Optional, Callable, Union
from functools import wraps

from app.shared.constants import UserRole
from ..models import User
from ..exceptions import PermissionDeniedException, InvalidRoleException, AdminRequiredException
from .auth import get_current_active_user


def check_user_permission(user: User, permission: str) -> bool:
    """
    Check if user has specific permission.
    
    Args:
        user: User object
        permission: Permission string to check
        
    Returns:
        bool: True if user has permission
    """
    return user.has_permission(permission)


def check_user_role(user: User, role: Union[str, UserRole]) -> bool:
    """
    Check if user has specific role.
    
    Args:
        user: User object
        role: Role to check (string or UserRole enum)
        
    Returns:
        bool: True if user has role
    """
    if isinstance(role, UserRole):
        role = role.value
    
    return user.role == role


def get_user_permissions(user: User) -> List[str]:
    """
    Get list of user permissions.
    
    Args:
        user: User object
        
    Returns:
        List[str]: List of user permissions
    """
    return user.get_permissions()


def require_permission(permission: str) -> Callable:
    """
    Dependency factory that requires specific permission.
    
    Args:
        permission: Required permission string
        
    Returns:
        Callable: FastAPI dependency function
    """
    def permission_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not check_user_permission(current_user, permission):
            raise PermissionDeniedException(
                required_permission=permission,
                user_permissions=get_user_permissions(current_user)
            )
        return current_user
    
    return permission_dependency


def require_role(role: Union[str, UserRole]) -> Callable:
    """
    Dependency factory that requires specific role.
    
    Args:
        role: Required role (string or UserRole enum)
        
    Returns:
        Callable: FastAPI dependency function
    """
    if isinstance(role, UserRole):
        role_str = role.value
    else:
        role_str = role
    
    def role_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if not check_user_role(current_user, role_str):
            raise PermissionDeniedException(
                message=f"Role '{role_str}' required",
                required_permission=f"role:{role_str}"
            )
        return current_user
    
    return role_dependency


def require_admin(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires admin role.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Admin user
        
    Raises:
        AdminRequiredException: If user is not admin
    """
    if not current_user.is_admin:
        raise AdminRequiredException()
    
    return current_user


def require_owner_or_admin(resource_user_id: int) -> Callable:
    """
    Dependency factory that requires resource ownership or admin role.
    
    Args:
        resource_user_id: ID of the user who owns the resource
        
    Returns:
        Callable: FastAPI dependency function
    """
    def owner_or_admin_dependency(
        current_user: User = Depends(get_current_active_user)
    ) -> User:
        if current_user.is_admin or current_user.id == resource_user_id:
            return current_user
        
        raise PermissionDeniedException(
            message="Resource access denied: must be owner or admin"
        )
    
    return owner_or_admin_dependency


class PermissionChecker:
    """Permission checker for complex authorization logic."""
    
    def __init__(self, user: User):
        self.user = user
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has permission."""
        return check_user_permission(self.user, permission)
    
    def has_role(self, role: Union[str, UserRole]) -> bool:
        """Check if user has role."""
        return check_user_role(self.user, role)
    
    def has_any_permission(self, permissions: List[str]) -> bool:
        """Check if user has any of the specified permissions."""
        return any(self.has_permission(perm) for perm in permissions)
    
    def has_all_permissions(self, permissions: List[str]) -> bool:
        """Check if user has all specified permissions."""
        return all(self.has_permission(perm) for perm in permissions)
    
    def has_any_role(self, roles: List[Union[str, UserRole]]) -> bool:
        """Check if user has any of the specified roles."""
        return any(self.has_role(role) for role in roles)
    
    def can_access_user_resource(self, resource_user_id: int) -> bool:
        """Check if user can access another user's resource."""
        return self.user.is_admin or self.user.id == resource_user_id
    
    def can_modify_user(self, target_user: User) -> bool:
        """Check if user can modify another user."""
        if self.user.is_admin:
            return not target_user.is_admin or self.user.id == target_user.id
        
        return self.user.id == target_user.id


def get_permission_checker(
    current_user: User = Depends(get_current_active_user)
) -> PermissionChecker:
    """
    Get permission checker for current user.
    
    Args:
        current_user: Current active user
        
    Returns:
        PermissionChecker: Permission checker instance
    """
    return PermissionChecker(current_user)


def require_any_permission(permissions: List[str]) -> Callable:
    """
    Dependency factory that requires any of the specified permissions.
    
    Args:
        permissions: List of acceptable permissions
        
    Returns:
        Callable: FastAPI dependency function
    """
    def any_permission_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> User:
        if not checker.has_any_permission(permissions):
            raise PermissionDeniedException(
                message=f"One of these permissions required: {', '.join(permissions)}",
                user_permissions=get_user_permissions(checker.user)
            )
        return checker.user
    
    return any_permission_dependency


def require_all_permissions(permissions: List[str]) -> Callable:
    """
    Dependency factory that requires all specified permissions.
    
    Args:
        permissions: List of required permissions
        
    Returns:
        Callable: FastAPI dependency function
    """
    def all_permissions_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> User:
        if not checker.has_all_permissions(permissions):
            raise PermissionDeniedException(
                message=f"All of these permissions required: {', '.join(permissions)}",
                user_permissions=get_user_permissions(checker.user)
            )
        return checker.user
    
    return all_permissions_dependency


def require_any_role(roles: List[Union[str, UserRole]]) -> Callable:
    """
    Dependency factory that requires any of the specified roles.
    
    Args:
        roles: List of acceptable roles
        
    Returns:
        Callable: FastAPI dependency function
    """
    role_strings = [role.value if isinstance(role, UserRole) else role for role in roles]
    
    def any_role_dependency(
        checker: PermissionChecker = Depends(get_permission_checker)
    ) -> User:
        if not checker.has_any_role(roles):
            raise PermissionDeniedException(
                message=f"One of these roles required: {', '.join(role_strings)}"
            )
        return checker.user
    
    return any_role_dependency