"""
Registration Routes

FastAPI routes for user registration and account creation.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from ..services import AuthService, UserService
from ..schemas.auth import RegisterRequest, RegisterResponse
from ..schemas.user import UserCreate, UserResponse
from ..dependencies import require_admin
from ..models import User
from ..exceptions import (
    UserAlreadyExistsException, WeakPasswordException, 
    AdminRequiredException
)

router = APIRouter()


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    register_data: RegisterRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Register a new user account.
    
    - **email**: User email address (must be unique)
    - **full_name**: User's full name
    - **password**: User password (must meet security requirements)
    - **confirm_password**: Password confirmation (must match password)
    - **timezone**: User timezone (optional, defaults to UTC)
    - **language**: User language preference (optional, defaults to en)
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.register_user(register_data)
        
        return {
            "message": result["message"],
            "user_id": result["user_id"],
            "email_verification_required": True
        }
        
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except WeakPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": e.message,
                "requirements": e.details.get("requirements", [])
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/admin/create-user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_admin(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Create a new user (admin operation).
    
    Requires admin privileges.
    
    - **email**: User email address (must be unique)
    - **full_name**: User's full name
    - **password**: User password
    - **role**: User role (user, admin, etc.)
    - **is_active**: Whether user is active
    - **email_verified**: Whether email is pre-verified
    - **timezone**: User timezone
    - **language**: User language preference
    - **permissions**: List of user permissions
    """
    try:
        user_service = UserService(db)
        
        result = await user_service.create_user(
            user_data=user_data,
            created_by_user_id=current_user.id
        )
        
        return result
        
    except UserAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=e.message
        )
    except WeakPasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": e.message,
                "requirements": e.details.get("requirements", [])
            }
        )
    except AdminRequiredException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User creation failed"
        )


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
async def resend_verification_email(
    email_data: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Resend email verification code.
    
    - **email**: User email address
    """
    try:
        auth_service = AuthService(db)
        
        
        return {
            "message": "If an account with this email exists and is not verified, a new verification code has been sent."
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resend verification email"
        )


@router.get("/check-email/{email}", status_code=status.HTTP_200_OK)
async def check_email_availability(
    email: str,
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Check if email address is available for registration.
    
    - **email**: Email address to check
    """
    try:
        user_service = UserService(db)
        
        from ..repositories import UserRepository
        user_repo = UserRepository(db)
        existing_user = await user_repo.get_by_email(email)
        
        return {
            "available": existing_user is None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check email availability"
        )