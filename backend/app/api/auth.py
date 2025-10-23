"""
Authentication API routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import (
    verify_password,
    get_password_hash,
    create_token_pair,
    verify_token,
    refresh_access_token
)
from app.models.user import User, UserSession
from app.utils.validators import UserCreate, UserLogin, APIResponse
from app.utils.exceptions import (
    AuthenticationError,
    UserNotFoundError,
    InvalidCredentialsError,
    TokenExpiredError
)

router = APIRouter()
security = HTTPBearer()


@router.post("/register", response_model=APIResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create new user
        hashed_password = get_password_hash(user_data.password)
        new_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password,
            account_type=user_data.account_type,
            company=user_data.company,
            job_title=user_data.job_title,
            is_verified=False  # Will be verified via email OTP
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return APIResponse(
            success=True,
            message="User registered successfully. Please verify your email.",
            data={
                "user_id": new_user.id,
                "email": new_user.email,
                "name": new_user.name
            }
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=APIResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT tokens
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise UserNotFoundError(login_data.email)
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise InvalidCredentialsError()
        
        # Check if user is active and verified
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated"
            )
        
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Please verify your email before logging in"
            )
        
        # Create JWT tokens
        tokens = create_token_pair(
            user_id=user.id,
            email=user.email,
            scopes=["read", "write"] if user.is_superuser else ["read"]
        )
        
        # Update last login
        user.last_login = func.now()
        db.commit()
        
        return APIResponse(
            success=True,
            message="Login successful",
            data={
                "access_token": tokens.access_token,
                "refresh_token": tokens.refresh_token,
                "token_type": tokens.token_type,
                "expires_in": tokens.expires_in,
                "user": user.to_dict()
            }
        )
        
    except (UserNotFoundError, InvalidCredentialsError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )


@router.post("/refresh", response_model=APIResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token
    """
    try:
        refresh_token = credentials.credentials
        
        # Generate new access token
        new_access_token = refresh_access_token(refresh_token)
        if not new_access_token:
            raise TokenExpiredError()
        
        return APIResponse(
            success=True,
            message="Token refreshed successfully",
            data={
                "access_token": new_access_token,
                "token_type": "bearer"
            }
        )
        
    except TokenExpiredError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout", response_model=APIResponse)
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Logout user and invalidate tokens
    """
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        
        if not token_data:
            raise TokenExpiredError()
        
        # In a production system, you would add the token to a blacklist
        # For now, we'll just return success
        
        return APIResponse(
            success=True,
            message="Logout successful"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Logout failed: {str(e)}"
        )


@router.get("/me", response_model=APIResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        
        if not token_data:
            raise TokenExpiredError()
        
        # Get user from database
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise UserNotFoundError(str(token_data.user_id))
        
        return APIResponse(
            success=True,
            message="User information retrieved successfully",
            data=user.to_dict()
        )
        
    except (TokenExpiredError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user information: {str(e)}"
        )


# Dependency to get current user
async def get_current_user_dependency(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user
    """
    try:
        token = credentials.credentials
        token_data = verify_token(token)
        
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is deactivated"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )