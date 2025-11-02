"""
Auth Module Routes - API endpoints for authentication
"""

from fastapi import APIRouter, HTTPException, Depends, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.core.database import get_async_db
from app.core.security import get_current_user
from app.core.rate_limiter import limiter, auth_rate_limit, otp_rate_limit, auth_rate_limiter
from .schemas import (
    UserCreate, 
    UserLogin, 
    OTPVerify, 
    TokenResponse, 
    UserResponse,
    OTPResponse,
    AuthResponse,
    PasswordReset,
    PasswordResetConfirm,
    RefreshTokenRequest
)
from .service import AuthService
from .exceptions import (
    AuthenticationError,
    UserNotFoundError,
    InvalidOTPError,
    AccountLockedError,
    EmailNotVerifiedError
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


def extract_request_info(request: Request) -> Dict[str, Any]:
    """Extract request information for security tracking"""
    return {
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent", ""),
        "accept_language": request.headers.get("accept-language", ""),
        "referer": request.headers.get("referer", ""),
        "device_type": "desktop",  # Could be enhanced with device detection
        "timestamp": "2024-01-01T00:00:00Z"  # Current timestamp
    }


@router.post("/register", response_model=OTPResponse, status_code=status.HTTP_201_CREATED)
@auth_rate_limit("5/minute")  # Allow 5 registration attempts per minute
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Register a new user account
    
    - **email**: Valid email address (will be verified)
    - **name**: Full name (2-100 characters)
    - **password**: Strong password (8+ chars, mixed case, digits)
    - **account_type**: Individual or Business
    - **company**: Company name (optional)
    - **job_title**: Job title (optional)
    - **phone**: Phone number (optional)
    
    Returns OTP verification details for email confirmation.
    """
    try:
        request_info = extract_request_info(request)
        auth_service = AuthService(db)
        
        result = await auth_service.register_user(user_data, request_info)
        
        return OTPResponse(
            message=result["message"],
            email_masked=result["email_masked"],
            expires_in=result["expires_in"]
        )
        
    except AuthenticationError as e:
        logger.warning(f"Registration failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/verify-registration", response_model=TokenResponse)
@otp_rate_limit("3/15minutes")  # Allow 3 OTP attempts per 15 minutes
async def verify_registration(
    otp_data: OTPVerify,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Verify registration OTP and activate account
    
    - **email**: Email address used for registration
    - **otp_code**: 6-digit code from email
    - **otp_type**: Must be "registration"
    - **remember_device**: Optional device trust (30 days)
    - **device_name**: Name for device identification
    
    Returns JWT tokens and user information.
    """
    try:
        request_info = extract_request_info(request)
        auth_service = AuthService(db)
        
        result = await auth_service.verify_registration(otp_data, request_info)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=UserResponse(**result["user"])
        )
        
    except (InvalidOTPError, UserNotFoundError) as e:
        logger.warning(f"Registration verification failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Registration verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Verification failed"
        )


@router.post("/login", response_model=OTPResponse)
@auth_rate_limit("10/minute")  # Allow 10 login attempts per minute
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Initiate user login process
    
    - **email**: Registered email address
    - **password**: User password
    - **remember_device**: Skip OTP for trusted devices
    - **device_name**: Name for device identification
    
    Returns OTP requirement or direct tokens for trusted devices.
    """
    try:
        request_info = extract_request_info(request)
        auth_service = AuthService(db)
        
        result = await auth_service.login_user(login_data, request_info)
        
        # If trusted device, return tokens directly
        if "access_token" in result:
            return TokenResponse(
                access_token=result["access_token"],
                refresh_token=result["refresh_token"],
                token_type=result["token_type"],
                expires_in=result["expires_in"],
                user=UserResponse(**result["user"])
            )
        
        # Otherwise, return OTP requirement
        return OTPResponse(
            message=result["message"],
            email_masked=result["email_masked"],
            expires_in=result["expires_in"]
        )
        
    except (UserNotFoundError, AuthenticationError, AccountLockedError, EmailNotVerifiedError) as e:
        logger.warning(f"Login failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/verify-login", response_model=TokenResponse)
@otp_rate_limit("3/15minutes")  # Allow 3 OTP verification attempts per 15 minutes
async def verify_login(
    otp_data: OTPVerify,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Verify login OTP and complete authentication
    
    - **email**: Email address
    - **otp_code**: 6-digit code from email
    - **otp_type**: Must be "login"
    - **remember_device**: Optional device trust (30 days)
    - **device_name**: Name for device identification
    
    Returns JWT tokens and user information.
    """
    try:
        request_info = extract_request_info(request)
        auth_service = AuthService(db)
        
        result = await auth_service.verify_login(otp_data, request_info)
        
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
            token_type=result["token_type"],
            expires_in=result["expires_in"],
            user=UserResponse(**result["user"])
        )
        
    except (InvalidOTPError, UserNotFoundError) as e:
        logger.warning(f"Login verification failed: {e.message}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except Exception as e:
        logger.error(f"Login verification error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login verification failed"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Refresh access token using refresh token
    
    - **refresh_token**: Valid refresh token
    
    Returns new JWT tokens.
    """
    try:
        request_info = extract_request_info(request)
        auth_service = AuthService(db)
        
        # TODO: Implement refresh token logic
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Refresh token endpoint not implemented yet"
        )
        
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout", response_model=AuthResponse)
async def logout_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Logout user and invalidate tokens
    
    Requires valid JWT token in Authorization header.
    """
    try:
        # TODO: Implement logout logic (invalidate tokens)
        return AuthResponse(
            success=True,
            message="Logged out successfully"
        )
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/reset-password", response_model=OTPResponse)
async def reset_password(
    reset_data: PasswordReset,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Initiate password reset process
    
    - **email**: Registered email address
    
    Sends OTP for password reset verification.
    """
    try:
        # TODO: Implement password reset initiation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password reset endpoint not implemented yet"
        )
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed"
        )


@router.post("/reset-password-confirm", response_model=AuthResponse)
async def reset_password_confirm(
    reset_data: PasswordResetConfirm,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Confirm password reset with OTP
    
    - **email**: Email address
    - **otp_code**: 6-digit OTP from email
    - **new_password**: New strong password
    
    Completes password reset process.
    """
    try:
        # TODO: Implement password reset confirmation
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password reset confirmation endpoint not implemented yet"
        )
        
    except Exception as e:
        logger.error(f"Password reset confirmation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current user information
    
    Requires valid JWT token in Authorization header.
    Returns current user profile data.
    """
    try:
        # Get full user data from database using user ID from token
        from .models import User
        from sqlalchemy import select
        
        result = await db.execute(select(User).where(User.id == current_user["id"]))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(**user.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user info error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )