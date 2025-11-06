"""
Password Routes

FastAPI routes for password management including password reset,
password change, and related security operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from ..services import AuthService, TokenService
from ..schemas.auth import (
    PasswordResetRequest, PasswordResetResponse, ChangePasswordRequest
)
from ..dependencies import get_current_active_user
from ..models import User
from ..exceptions import (
    InvalidCredentialsException, WeakPasswordException, 
    SamePasswordException, InvalidOTPException, OTPExpiredException,
    UserNotFoundException
)

router = APIRouter()


@router.post("/password/reset-request", response_model=PasswordResetResponse, status_code=status.HTTP_200_OK)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Request password reset for user account.
    
    Sends a password reset code to the user's email if the account exists.
    Always returns success for security reasons (doesn't reveal if email exists).
    
    - **email**: User email address
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.request_password_reset(reset_data.email)
        
        return result
        
    except Exception as e:
        return {
            "message": "If an account with this email exists, you will receive a password reset code."
        }


@router.post("/password/reset", status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """
    Reset password using OTP code.
    
    - **email**: User email address
    - **otp_code**: Password reset code received via email
    - **new_password**: New password (must meet security requirements)
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.reset_password(
            email=reset_data["email"],
            otp_code=reset_data["otp_code"],
            new_password=reset_data["new_password"]
        )
        
        return result
        
    except (InvalidOTPException, OTPExpiredException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    except UserNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(
    change_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Change user password (authenticated users only).
    
    Requires valid authentication token.
    
    - **current_password**: Current user password
    - **new_password**: New password (must meet security requirements)
    - **confirm_password**: New password confirmation (must match new_password)
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.change_password(
            user_id=current_user.id,
            change_data=change_data
        )
        
        return result
        
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
    except SamePasswordException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed"
        )


@router.get("/password/strength/{password}", status_code=status.HTTP_200_OK)
async def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Check password strength and return requirements.
    
    - **password**: Password to check
    """
    try:
        requirements = []
        score = 0
        
        if len(password) >= 8:
            score += 1
        else:
            requirements.append("At least 8 characters")
        
        if any(c.isupper() for c in password):
            score += 1
        else:
            requirements.append("At least one uppercase letter")
        
        if any(c.islower() for c in password):
            score += 1
        else:
            requirements.append("At least one lowercase letter")
        
        if any(c.isdigit() for c in password):
            score += 1
        else:
            requirements.append("At least one number")
        
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            score += 1
        else:
            requirements.append("At least one special character")
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(score, 4)]
        
        return {
            "strength": strength,
            "score": score,
            "max_score": 5,
            "is_valid": len(requirements) == 0,
            "missing_requirements": requirements
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password strength check failed"
        )


@router.post("/password/validate-reset-code", status_code=status.HTTP_200_OK)
async def validate_reset_code(
    validation_data: Dict[str, str],
    db: Session = Depends(get_db)
) -> Dict[str, bool]:
    """
    Validate password reset code without using it.
    
    - **email**: User email address
    - **otp_code**: Password reset code to validate
    """
    try:
        token_service = TokenService(db)
        
        from ..repositories import UserRepository
        user_repo = UserRepository(db)
        user = await user_repo.get_by_email(validation_data["email"])
        
        if not user:
            return {"valid": False}
        
        from ..repositories import TokenRepository
        token_repo = TokenRepository(db)
        otp = await token_repo.get_valid_otp(
            user.id, 
            validation_data["otp_code"], 
            "password_reset"
        )
        
        return {
            "valid": otp is not None and otp.is_valid
        }
        
    except Exception as e:
        return {"valid": False}


@router.get("/password/policy", status_code=status.HTTP_200_OK)
async def get_password_policy() -> Dict[str, Any]:
    """
    Get current password policy requirements.
    
    Public endpoint that returns password requirements.
    """
    return {
        "minimum_length": 8,
        "require_uppercase": True,
        "require_lowercase": True,
        "require_numbers": True,
        "require_special_characters": False,
        "special_characters": "!@#$%^&*()_+-=[]{}|;:,.<>?",
        "description": "Password must be at least 8 characters long and contain uppercase, lowercase, and numeric characters."
    }