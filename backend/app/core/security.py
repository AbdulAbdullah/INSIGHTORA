"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """Token data model"""
    user_id: Optional[int] = None
    email: Optional[str] = None
    scopes: list[str] = []


class Token(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password
    """
    return pwd_context.hash(password)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT refresh token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[TokenData]:
    """
    Verify and decode JWT token
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Check token type
        if payload.get("type") != token_type:
            return None
            
        user_id: int = payload.get("sub")
        email: str = payload.get("email")
        scopes: list = payload.get("scopes", [])
        
        if user_id is None:
            return None
            
        token_data = TokenData(
            user_id=user_id,
            email=email,
            scopes=scopes
        )
        
        return token_data
        
    except JWTError:
        return None


def create_token_pair(user_id: int, email: str, scopes: list[str] = None) -> Token:
    """
    Create access and refresh token pair
    """
    if scopes is None:
        scopes = []
    
    # Common token data
    token_data = {
        "sub": str(user_id),
        "email": email,
        "scopes": scopes
    }
    
    # Create tokens
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Create new access token from refresh token
    """
    token_data = verify_token(refresh_token, token_type="refresh")
    
    if token_data is None:
        return None
    
    # Create new access token with same data
    new_token_data = {
        "sub": str(token_data.user_id),
        "email": token_data.email,
        "scopes": token_data.scopes
    }
    
    return create_access_token(new_token_data)


def generate_api_key() -> str:
    """
    Generate API key for service-to-service communication
    """
    import secrets
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for storage
    """
    return get_password_hash(api_key)


def verify_api_key(api_key: str, hashed_api_key: str) -> bool:
    """
    Verify API key against its hash
    """
    return verify_password(api_key, hashed_api_key)