"""
User Repository

Data access layer for User model operations.
Handles all database interactions for user management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

from ..models import User
from ..exceptions import UserNotFoundException, UserAlreadyExistsException
from app.shared.constants import UserRole


class UserRepository:
    """Repository for User model database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize user repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def create_user(self, user_data: Dict[str, Any]) -> User:
        """
        Create a new user.
        
        Args:
            user_data: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            UserAlreadyExistsException: If user with email already exists
        """
        existing_user = await self.get_by_email(user_data.get("email"))
        if existing_user:
            raise UserAlreadyExistsException(email=user_data.get("email"))
        
        user = User(**user_data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Optional[User]: User object if found
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: Email address
            
        Returns:
            Optional[User]: User object if found
        """
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_by_id_or_raise(self, user_id: int) -> User:
        """
        Get user by ID or raise exception.
        
        Args:
            user_id: User ID
            
        Returns:
            User: User object
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_identifier=str(user_id))
        return user
    
    async def get_by_email_or_raise(self, email: str) -> User:
        """
        Get user by email or raise exception.
        
        Args:
            email: Email address
            
        Returns:
            User: User object
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_by_email(email)
        if not user:
            raise UserNotFoundException(user_identifier=email)
        return user
    
    async def update_user(self, user_id: int, update_data: Dict[str, Any]) -> User:
        """
        Update user information.
        
        Args:
            user_id: User ID
            update_data: Data to update
            
        Returns:
            User: Updated user object
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_by_id_or_raise(user_id)
        
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.get_by_id_or_raise(user_id)
        
        self.db.delete(user)
        self.db.commit()
        
        return True
    
    async def get_users_paginated(
        self,
        page: int = 1,
        per_page: int = 10,
        search_query: Optional[str] = None,
        role_filter: Optional[str] = None,
        is_active: Optional[bool] = None,
        email_verified: Optional[bool] = None
    ) -> Tuple[List[User], int]:
        """
        Get paginated list of users with filters.
        
        Args:
            page: Page number (1-based)
            per_page: Items per page
            search_query: Search in name and email
            role_filter: Filter by role
            is_active: Filter by active status
            email_verified: Filter by email verification
            
        Returns:
            Tuple[List[User], int]: List of users and total count
        """
        query = self.db.query(User)
        
        if search_query:
            search_term = f"%{search_query}%"
            query = query.filter(
                or_(
                    User.full_name.ilike(search_term),
                    User.email.ilike(search_term)
                )
            )
        
        if role_filter:
            query = query.filter(User.role == role_filter)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if email_verified is not None:
            query = query.filter(User.email_verified == email_verified)
        
        total = query.count()
        
        users = (
            query
            .order_by(desc(User.created_at))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
        
        return users, total
    
    async def get_active_users_count(self) -> int:
        """
        Get count of active users.
        
        Returns:
            int: Number of active users
        """
        return self.db.query(User).filter(User.is_active == True).count()
    
    async def get_users_by_role(self, role: str) -> List[User]:
        """
        Get all users with specific role.
        
        Args:
            role: User role
            
        Returns:
            List[User]: List of users with the role
        """
        return self.db.query(User).filter(User.role == role).all()
    
    async def get_unverified_users(self, days_old: int = 7) -> List[User]:
        """
        Get users with unverified emails older than specified days.
        
        Args:
            days_old: Number of days since registration
            
        Returns:
            List[User]: List of unverified users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        return (
            self.db.query(User)
            .filter(
                and_(
                    User.email_verified == False,
                    User.created_at <= cutoff_date
                )
            )
            .all()
        )
    
    async def get_inactive_users(self, days_inactive: int = 30) -> List[User]:
        """
        Get users inactive for specified days.
        
        Args:
            days_inactive: Number of days of inactivity
            
        Returns:
            List[User]: List of inactive users
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_inactive)
        
        return (
            self.db.query(User)
            .filter(
                or_(
                    User.last_login_at.is_(None),
                    User.last_login_at <= cutoff_date
                )
            )
            .filter(User.is_active == True)
            .all()
        )
    
    async def update_last_login(self, user_id: int) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user_id: User ID
        """
        self.db.query(User).filter(User.id == user_id).update({
            User.last_login_at: datetime.utcnow()
        })
        self.db.commit()
    
    async def verify_email(self, user_id: int) -> User:
        """
        Mark user's email as verified.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user object
        """
        user = await self.get_by_id_or_raise(user_id)
        user.verify_email()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def update_password_timestamp(self, user_id: int) -> None:
        """
        Update user's password change timestamp.
        
        Args:
            user_id: User ID
        """
        self.db.query(User).filter(User.id == user_id).update({
            User.password_changed_at: datetime.utcnow()
        })
        self.db.commit()
    
    async def enable_two_factor(self, user_id: int) -> User:
        """
        Enable two-factor authentication for user.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user object
        """
        user = await self.get_by_id_or_raise(user_id)
        user.enable_two_factor()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def disable_two_factor(self, user_id: int) -> User:
        """
        Disable two-factor authentication for user.
        
        Args:
            user_id: User ID
            
        Returns:
            User: Updated user object
        """
        user = await self.get_by_id_or_raise(user_id)
        user.disable_two_factor()
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def add_permission(self, user_id: int, permission: str) -> User:
        """
        Add permission to user.
        
        Args:
            user_id: User ID
            permission: Permission to add
            
        Returns:
            User: Updated user object
        """
        user = await self.get_by_id_or_raise(user_id)
        user.add_permission(permission)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def remove_permission(self, user_id: int, permission: str) -> User:
        """
        Remove permission from user.
        
        Args:
            user_id: User ID
            permission: Permission to remove
            
        Returns:
            User: Updated user object
        """
        user = await self.get_by_id_or_raise(user_id)
        user.remove_permission(permission)
        
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    async def get_user_statistics(self) -> Dict[str, Any]:
        """
        Get user statistics.
        
        Returns:
            Dict[str, Any]: User statistics
        """
        total_users = self.db.query(User).count()
        active_users = self.db.query(User).filter(User.is_active == True).count()
        verified_users = self.db.query(User).filter(User.email_verified == True).count()
        admin_users = self.db.query(User).filter(User.role == UserRole.ADMIN.value).count()
        
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_registrations = (
            self.db.query(User)
            .filter(User.created_at >= thirty_days_ago)
            .count()
        )
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "verified_users": verified_users,
            "admin_users": admin_users,
            "recent_registrations": recent_registrations,
            "verification_rate": (verified_users / total_users * 100) if total_users > 0 else 0
        }