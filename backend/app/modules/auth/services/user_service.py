"""
User Service

Business logic for user management including profile updates,
permission management, and administrative operations.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import secrets
from passlib.context import CryptContext

from ..repositories import UserRepository, TokenRepository
from ..models import User
from ..schemas.user import UserCreate, UserUpdate, UserSearch
from ..exceptions import (
    UserNotFoundException, UserAlreadyExistsException, PermissionDeniedException,
    InvalidRoleException, WeakPasswordException, ProfileUpdateException,
    AdminRequiredException
)
from app.shared.constants import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize user service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
    
    
    async def create_user(self, user_data: UserCreate, created_by_user_id: int) -> Dict[str, Any]:
        """
        Create a new user (admin operation).
        
        Args:
            user_data: User creation data
            created_by_user_id: ID of user creating this user
            
        Returns:
            Dict[str, Any]: Created user information
            
        Raises:
            UserAlreadyExistsException: If user already exists
            AdminRequiredException: If creator is not admin
            WeakPasswordException: If password is weak
        """
        creator = await self.user_repo.get_by_id_or_raise(created_by_user_id)
        if not creator.is_admin:
            raise AdminRequiredException(operation="create_user")
        
        await self._validate_password_strength(user_data.password)
        
        hashed_password = pwd_context.hash(user_data.password)
        
        create_data = {
            "email": user_data.email,
            "full_name": user_data.full_name,
            "hashed_password": hashed_password,
            "role": user_data.role,
            "is_active": user_data.is_active,
            "email_verified": user_data.email_verified,
            "timezone": user_data.timezone,
            "language": user_data.language
        }
        
        user = await self.user_repo.create_user(create_data)
        
        if user_data.permissions:
            for permission in user_data.permissions:
                await self.user_repo.add_permission(user.id, permission)
        
        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "created_at": user.created_at,
            "message": "User created successfully"
        }
    
    async def get_user_by_id(self, user_id: int, requesting_user_id: int) -> Dict[str, Any]:
        """
        Get user by ID with authorization check.
        
        Args:
            user_id: User ID to retrieve
            requesting_user_id: ID of user making the request
            
        Returns:
            Dict[str, Any]: User information
            
        Raises:
            UserNotFoundException: If user not found
            PermissionDeniedException: If access denied
        """
        requesting_user = await self.user_repo.get_by_id_or_raise(requesting_user_id)
        
        user = await self.user_repo.get_by_id_or_raise(user_id)
        
        if not requesting_user.is_admin and requesting_user.id != user_id:
            raise PermissionDeniedException(message="Can only view own profile or admin required")
        
        return {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
            "email_verified": user.email_verified,
            "email_verified_at": user.email_verified_at,
            "timezone": user.timezone,
            "language": user.language,
            "avatar_url": user.avatar_url,
            "two_factor_enabled": user.two_factor_enabled,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login_at": user.last_login_at,
            "permissions": user.get_permissions()
        }
    
    async def update_user(
        self, 
        user_id: int, 
        update_data: UserUpdate, 
        updating_user_id: int
    ) -> Dict[str, Any]:
        """
        Update user information.
        
        Args:
            user_id: User ID to update
            update_data: Update data
            updating_user_id: ID of user making the update
            
        Returns:
            Dict[str, Any]: Updated user information
            
        Raises:
            UserNotFoundException: If user not found
            PermissionDeniedException: If access denied
        """
        updating_user = await self.user_repo.get_by_id_or_raise(updating_user_id)
        
        target_user = await self.user_repo.get_by_id_or_raise(user_id)
        
        can_update = (
            updating_user.is_admin or 
            updating_user.id == user_id
        )
        
        if not can_update:
            raise PermissionDeniedException(message="Can only update own profile or admin required")
        
        update_fields = {}
        
        self_updatable_fields = ["full_name", "timezone", "language", "avatar_url"]
        
        admin_only_fields = ["role", "is_active", "email_verified", "two_factor_enabled"]
        
        for field, value in update_data.dict(exclude_unset=True).items():
            if field in self_updatable_fields:
                update_fields[field] = value
            elif field in admin_only_fields:
                if not updating_user.is_admin:
                    raise PermissionDeniedException(
                        message=f"Admin required to update field: {field}"
                    )
                update_fields[field] = value
        
        updated_user = await self.user_repo.update_user(user_id, update_fields)
        
        return {
            "user_id": updated_user.id,
            "updated_fields": list(update_fields.keys()),
            "message": "User updated successfully"
        }
    
    async def delete_user(self, user_id: int, deleting_user_id: int) -> Dict[str, Any]:
        """
        Delete user (admin operation).
        
        Args:
            user_id: User ID to delete
            deleting_user_id: ID of user performing deletion
            
        Returns:
            Dict[str, Any]: Deletion result
            
        Raises:
            UserNotFoundException: If user not found
            AdminRequiredException: If deleting user is not admin
            PermissionDeniedException: If trying to delete another admin
        """
        deleting_user = await self.user_repo.get_by_id_or_raise(deleting_user_id)
        
        if not deleting_user.is_admin:
            raise AdminRequiredException(operation="delete_user")
        
        target_user = await self.user_repo.get_by_id_or_raise(user_id)
        
        if target_user.is_admin and target_user.id != deleting_user.id:
            raise PermissionDeniedException(message="Cannot delete other admin users")
        
        await self.token_repo.revoke_all_user_devices(user_id)
        
        await self.user_repo.delete_user(user_id)
        
        return {
            "user_id": user_id,
            "deleted": True,
            "message": "User deleted successfully"
        }
    
    
    async def search_users(
        self, 
        search_params: UserSearch, 
        requesting_user_id: int
    ) -> Dict[str, Any]:
        """
        Search users with pagination.
        
        Args:
            search_params: Search parameters
            requesting_user_id: ID of user making the request
            
        Returns:
            Dict[str, Any]: Search results with pagination
            
        Raises:
            AdminRequiredException: If requesting user is not admin
        """
        requesting_user = await self.user_repo.get_by_id_or_raise(requesting_user_id)
        if not requesting_user.is_admin:
            raise AdminRequiredException(operation="search_users")
        
        users, total = await self.user_repo.get_users_paginated(
            page=search_params.page,
            per_page=search_params.per_page,
            search_query=search_params.query,
            role_filter=search_params.role,
            is_active=search_params.is_active,
            email_verified=search_params.email_verified
        )
        
        pages = (total + search_params.per_page - 1) // search_params.per_page
        
        return {
            "users": [
                {
                    "id": user.id,
                    "email": user.email,
                    "full_name": user.full_name,
                    "role": user.role,
                    "is_active": user.is_active,
                    "email_verified": user.email_verified,
                    "created_at": user.created_at,
                    "last_login_at": user.last_login_at
                }
                for user in users
            ],
            "pagination": {
                "total": total,
                "page": search_params.page,
                "per_page": search_params.per_page,
                "pages": pages,
                "has_next": search_params.page < pages,
                "has_prev": search_params.page > 1
            }
        }
    
    
    async def add_user_permission(
        self, 
        user_id: int, 
        permission: str, 
        granting_user_id: int
    ) -> Dict[str, Any]:
        """
        Add permission to user.
        
        Args:
            user_id: User ID
            permission: Permission to add
            granting_user_id: ID of user granting permission
            
        Returns:
            Dict[str, Any]: Permission addition result
        """
        granting_user = await self.user_repo.get_by_id_or_raise(granting_user_id)
        if not granting_user.is_admin:
            raise AdminRequiredException(operation="add_permission")
        
        updated_user = await self.user_repo.add_permission(user_id, permission)
        
        return {
            "user_id": user_id,
            "permission": permission,
            "added": True,
            "current_permissions": updated_user.get_permissions(),
            "message": f"Permission '{permission}' added successfully"
        }
    
    async def remove_user_permission(
        self, 
        user_id: int, 
        permission: str, 
        revoking_user_id: int
    ) -> Dict[str, Any]:
        """
        Remove permission from user.
        
        Args:
            user_id: User ID
            permission: Permission to remove
            revoking_user_id: ID of user revoking permission
            
        Returns:
            Dict[str, Any]: Permission removal result
        """
        revoking_user = await self.user_repo.get_by_id_or_raise(revoking_user_id)
        if not revoking_user.is_admin:
            raise AdminRequiredException(operation="remove_permission")
        
        updated_user = await self.user_repo.remove_permission(user_id, permission)
        
        return {
            "user_id": user_id,
            "permission": permission,
            "removed": True,
            "current_permissions": updated_user.get_permissions(),
            "message": f"Permission '{permission}' removed successfully"
        }
    
    async def get_user_permissions(self, user_id: int, requesting_user_id: int) -> Dict[str, Any]:
        """
        Get user permissions.
        
        Args:
            user_id: User ID
            requesting_user_id: ID of user making the request
            
        Returns:
            Dict[str, Any]: User permissions
        """
        requesting_user = await self.user_repo.get_by_id_or_raise(requesting_user_id)
        
        if not requesting_user.is_admin and requesting_user.id != user_id:
            raise PermissionDeniedException(message="Can only view own permissions or admin required")
        
        user = await self.user_repo.get_by_id_or_raise(user_id)
        
        return {
            "user_id": user_id,
            "role": user.role,
            "permissions": user.get_permissions(),
            "is_admin": user.is_admin
        }
    
    
    async def get_user_statistics(self, requesting_user_id: int) -> Dict[str, Any]:
        """
        Get user statistics (admin only).
        
        Args:
            requesting_user_id: ID of user requesting statistics
            
        Returns:
            Dict[str, Any]: User statistics
        """
        requesting_user = await self.user_repo.get_by_id_or_raise(requesting_user_id)
        if not requesting_user.is_admin:
            raise AdminRequiredException(operation="view_statistics")
        
        return await self.user_repo.get_user_statistics()
    
    async def get_inactive_users(
        self, 
        days_inactive: int, 
        requesting_user_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get inactive users (admin only).
        
        Args:
            days_inactive: Number of days of inactivity
            requesting_user_id: ID of user making the request
            
        Returns:
            List[Dict[str, Any]]: List of inactive users
        """
        requesting_user = await self.user_repo.get_by_id_or_raise(requesting_user_id)
        if not requesting_user.is_admin:
            raise AdminRequiredException(operation="view_inactive_users")
        
        inactive_users = await self.user_repo.get_inactive_users(days_inactive)
        
        return [
            {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "last_login_at": user.last_login_at,
                "created_at": user.created_at,
                "days_inactive": (datetime.utcnow() - (user.last_login_at or user.created_at)).days
            }
            for user in inactive_users
        ]
    
    
    async def update_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update user profile (self-service).
        
        Args:
            user_id: User ID
            profile_data: Profile update data
            
        Returns:
            Dict[str, Any]: Profile update result
        """
        allowed_fields = ["full_name", "timezone", "language", "avatar_url"]
        
        update_data = {
            field: value for field, value in profile_data.items()
            if field in allowed_fields and value is not None
        }
        
        if not update_data:
            raise ProfileUpdateException(reason="No valid fields to update")
        
        updated_user = await self.user_repo.update_user(user_id, update_data)
        
        return {
            "user_id": user_id,
            "updated_fields": list(update_data.keys()),
            "profile": {
                "full_name": updated_user.full_name,
                "timezone": updated_user.timezone,
                "language": updated_user.language,
                "avatar_url": updated_user.avatar_url
            },
            "message": "Profile updated successfully"
        }
    
    
    async def _validate_password_strength(self, password: str) -> None:
        """Validate password strength."""
        requirements = []
        
        if len(password) < 8:
            requirements.append("At least 8 characters")
        
        if not any(c.isupper() for c in password):
            requirements.append("At least one uppercase letter")
        
        if not any(c.islower() for c in password):
            requirements.append("At least one lowercase letter")
        
        if not any(c.isdigit() for c in password):
            requirements.append("At least one number")
        
        if requirements:
            raise WeakPasswordException(requirements=requirements)