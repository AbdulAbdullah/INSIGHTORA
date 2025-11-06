"""
Authentication Dependencies

FastAPI dependencies for user authentication, token validation,
and session management.
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime

from app.core.database import get_db
from app.core.config import get_settings
from ..models import User, DeviceTrust
from ..exceptions import (
    InvalidTokenException, TokenExpiredException, UserNotFoundException,
    InactiveUserException, EmailNotVerifiedException, DeviceNotTrustedException
)

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    """
    Verify JWT token and return payload.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        dict: Token payload
        
    Raises:
        InvalidTokenException: If token is invalid
        TokenExpiredException: If token is expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise TokenExpiredException()
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.InvalidTokenError:
        raise InvalidTokenException()


async def get_current_user(
    token_payload: dict = Depends(verify_token),
    db: Session = Depends(get_db)
) -> User:
    """
    Get current authenticated user from token.
    
    Args:
        token_payload: Verified token payload
        db: Database session
        
    Returns:
        User: Current user object
        
    Raises:
        UserNotFoundException: If user not found
    """
    user_id = token_payload.get("sub")
    if not user_id:
        raise InvalidTokenException("Invalid token payload")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise UserNotFoundException(user_identifier=str(user_id))
    
    user.update_last_login()
    db.commit()
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (must be active).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: Active user object
        
    Raises:
        InactiveUserException: If user is inactive
    """
    if not current_user.is_active:
        raise InactiveUserException(user_id=current_user.id)
    
    return current_user


async def get_current_verified_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Get current verified user (must have verified email).
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Verified user object
        
    Raises:
        EmailNotVerifiedException: If email not verified
    """
    if not current_user.email_verified:
        raise EmailNotVerifiedException(email=current_user.email)
    
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Optional[User]: User object if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token_payload = await verify_token(credentials)
        user_id = token_payload.get("sub")
        
        if user_id:
            user = db.query(User).filter(User.id == user_id).first()
            if user and user.is_active:
                return user
                
    except Exception:
        pass
    
    return None


def require_auth(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires authentication.
    
    Args:
        current_user: Current active user
        
    Returns:
        User: Authenticated user
    """
    return current_user


def require_verified_email(
    current_user: User = Depends(get_current_verified_user)
) -> User:
    """
    Dependency that requires verified email.
    
    Args:
        current_user: Current verified user
        
    Returns:
        User: Verified user
    """
    return current_user


async def require_two_factor(
    token_payload: dict = Depends(verify_token),
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency that requires two-factor authentication.
    
    Args:
        token_payload: Verified token payload
        current_user: Current active user
        
    Returns:
        User: User with 2FA verified
        
    Raises:
        HTTPException: If 2FA not completed
    """
    if not current_user.two_factor_enabled:
        return current_user
    
    two_factor_verified = token_payload.get("2fa_verified", False)
    if not two_factor_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Two-factor authentication required"
        )
    
    return current_user


async def get_device_trust(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Optional[DeviceTrust]:
    """
    Get device trust for current request.
    
    Args:
        request: FastAPI request object
        current_user: Current active user
        db: Database session
        
    Returns:
        Optional[DeviceTrust]: Device trust if exists and valid
    """
    device_token = request.headers.get("X-Device-Token")
    if not device_token:
        device_token = request.cookies.get("device_token")
    
    if not device_token:
        return None
    
    device_trust = db.query(DeviceTrust).filter(
        DeviceTrust.device_token == device_token,
        DeviceTrust.user_id == current_user.id
    ).first()
    
    if not device_trust or not device_trust.is_valid:
        return None
    
    device_trust.update_last_used()
    db.commit()
    
    return device_trust


async def require_trusted_device(
    device_trust: Optional[DeviceTrust] = Depends(get_device_trust)
) -> DeviceTrust:
    """
    Dependency that requires a trusted device.
    
    Args:
        device_trust: Device trust object
        
    Returns:
        DeviceTrust: Valid device trust
        
    Raises:
        DeviceNotTrustedException: If device not trusted
    """
    if not device_trust:
        raise DeviceNotTrustedException()
    
    return device_trust


class AuthContext:
    """Authentication context for dependency injection."""
    
    def __init__(
        self,
        user: Optional[User] = None,
        device_trust: Optional[DeviceTrust] = None,
        token_payload: Optional[dict] = None
    ):
        self.user = user
        self.device_trust = device_trust
        self.token_payload = token_payload
        self.is_authenticated = user is not None
        self.is_verified = user.email_verified if user else False
        self.is_admin = user.is_admin if user else False


async def get_auth_context(
    user: Optional[User] = Depends(get_optional_user),
    device_trust: Optional[DeviceTrust] = Depends(get_device_trust),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> AuthContext:
    """
    Get complete authentication context.
    
    Args:
        user: Optional current user
        device_trust: Optional device trust
        credentials: Optional credentials
        
    Returns:
        AuthContext: Complete auth context
    """
    token_payload = None
    if credentials:
        try:
            token_payload = await verify_token(credentials)
        except Exception:
            pass
    
    return AuthContext(
        user=user,
        device_trust=device_trust,
        token_payload=token_payload
    )