"""
Login Routes

FastAPI routes for user authentication including login, logout,
token refresh, and email verification.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from ..services import AuthService
from ..schemas.auth import (
    LoginRequest, LoginResponse, RefreshTokenRequest, RefreshTokenResponse,
    VerifyEmailRequest, VerifyEmailResponse
)
from ..dependencies import get_current_user, get_current_active_user
from ..models import User
from ..exceptions import (
    InvalidCredentialsException, TwoFactorRequiredException, 
    EmailNotVerifiedException, InactiveUserException
)

router = APIRouter()


@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Authenticate user and return access tokens.
    
    - **email**: User email address
    - **password**: User password
    - **remember_device**: Whether to remember this device
    - **otp_code**: Two-factor authentication code (if required)
    - **device_name**: Name for this device (if remembering)
    """
    try:
        auth_service = AuthService(db)
        
        ip_address = request.client.host
        user_agent = request.headers.get("user-agent")
        
        result = await auth_service.login_user(
            login_data=login_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if result.get("device_token"):
            response.set_cookie(
                key="device_token",
                value=result["device_token"],
                max_age=30 * 24 * 60 * 60,
                httponly=True,
                secure=True,
                samesite="lax"
            )
        
        return result
        
    except TwoFactorRequiredException as e:
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail={
                "message": e.message,
                "requires_2fa": True,
                "otp_type": e.details.get("otp_type")
            }
        )
    except (InvalidCredentialsException, InactiveUserException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshTokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid JWT refresh token
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.refresh_token(refresh_data.refresh_token)
        
        return result
        
    except InvalidCredentialsException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/verify-email", response_model=VerifyEmailResponse, status_code=status.HTTP_200_OK)
async def verify_email(
    verify_data: VerifyEmailRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify user email address with OTP code.
    
    - **email**: User email address
    - **otp_code**: Email verification code
    """
    try:
        auth_service = AuthService(db)
        
        result = await auth_service.verify_email(
            email=verify_data.email,
            otp_code=verify_data.otp_code
        )
        
        return result
        
    except (InvalidCredentialsException, EmailNotVerifiedException) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed"
        )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    response: Response,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, str]:
    """
    Logout user and clear device trust cookie.
    
    Requires valid authentication token.
    """
    try:
        response.delete_cookie(
            key="device_token",
            httponly=True,
            secure=True,
            samesite="lax"
        )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current authenticated user information.
    
    Requires valid authentication token.
    """
    try:
        return {
            "id": current_user.id,
            "email": current_user.email,
            "full_name": current_user.full_name,
            "role": current_user.role,
            "is_active": current_user.is_active,
            "email_verified": current_user.email_verified,
            "timezone": current_user.timezone,
            "language": current_user.language,
            "avatar_url": current_user.avatar_url,
            "two_factor_enabled": current_user.two_factor_enabled,
            "created_at": current_user.created_at,
            "last_login_at": current_user.last_login_at,
            "permissions": current_user.get_permissions()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.get("/status", status_code=status.HTTP_200_OK)
async def auth_status() -> Dict[str, Any]:
    """
    Get authentication service status.
    
    Public endpoint for health checks.
    """
    return {
        "service": "authentication",
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    }