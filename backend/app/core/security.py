"""
Security Utilities

JWT, hashing, encryption utilities following security best practices.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from jose import JWTError, jwt
import secrets
import hashlib
from cryptography.fernet import Fernet
import base64
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_encryption_key = None


def get_encryption_key() -> bytes:
    """Get or generate encryption key for sensitive data."""
    global _encryption_key
    if _encryption_key is None:
        key_material = settings.SECRET_KEY.encode()
        _encryption_key = base64.urlsafe_b64encode(
            hashlib.sha256(key_material).digest()
        )
    return _encryption_key


def encrypt_sensitive_data(data: str) -> str:
    """
    Encrypt sensitive data like database credentials.
    
    Args:
        data: Plain text data to encrypt
        
    Returns:
        str: Encrypted data as base64 string
    """
    try:
        fernet = Fernet(get_encryption_key())
        encrypted_data = fernet.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        raise


def decrypt_sensitive_data(encrypted_data: str) -> str:
    """
    Decrypt sensitive data.
    
    Args:
        encrypted_data: Base64 encoded encrypted data
        
    Returns:
        str: Decrypted plain text data
    """
    try:
        fernet = Fernet(get_encryption_key())
        decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = fernet.decrypt(decoded_data)
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


def generate_otp(length: int = 6) -> str:
    """
    Generate a secure OTP.
    
    Args:
        length: Length of OTP (default 6)
        
    Returns:
        str: Generated OTP
    """
    return ''.join([str(secrets.randbelow(10)) for _ in range(length)])


def generate_device_token() -> str:
    """
    Generate a secure device trust token.
    
    Returns:
        str: Device token
    """
    return secrets.token_urlsafe(32)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Token expiration time
        
    Returns:
        str: JWT token
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


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create JWT refresh token.
    
    Args:
        data: Data to encode in token
        
    Returns:
        str: JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.REFRESH_SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token to verify
        token_type: Type of token ("access" or "refresh")
        
    Returns:
        Dict containing token payload or None if invalid
    """
    try:
        secret_key = (
            settings.SECRET_KEY if token_type == "access" 
            else settings.REFRESH_SECRET_KEY
        )
        
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[settings.ALGORITHM]
        )
        
        if payload.get("type") != token_type:
            return None
            
        return payload
        
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None


def generate_api_key() -> str:
    """
    Generate API key for external integrations.
    
    Returns:
        str: API key
    """
    return f"sk_{secrets.token_urlsafe(32)}"


def hash_api_key(api_key: str) -> str:
    """
    Hash API key for storage.
    
    Args:
        api_key: Plain API key
        
    Returns:
        str: Hashed API key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(plain_key: str, hashed_key: str) -> bool:
    """
    Verify API key against its hash.
    
    Args:
        plain_key: Plain API key
        hashed_key: Hashed API key
        
    Returns:
        bool: True if key matches
    """
    return hash_api_key(plain_key) == hashed_key