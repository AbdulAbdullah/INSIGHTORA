"""
Authentication Service

Business logic for authentication operations including login, registration,
password management, and session handling.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import secrets
import hashlib
import jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from ..repositories import UserRepository, TokenRepository
from ..models import User, OTP, DeviceTrust
from ..schemas.auth import LoginRequest, RegisterRequest, ChangePasswordRequest
from ..exceptions import (
    InvalidCredentialsException, AccountLockedException, TwoFactorRequiredException,
    InvalidOTPException, OTPExpiredException, EmailNotVerifiedException,
    InactiveUserException, UserAlreadyExistsException, WeakPasswordException,
    PasswordMismatchException, SamePasswordException
)

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        """
        Initialize authentication service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.user_repo = UserRepository(db)
        self.token_repo = TokenRepository(db)
        self.max_login_attempts = 5
        self.lockout_duration_minutes = 15
    
    async def register_user(self, register_data: RegisterRequest) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            register_data: Registration request data
            
        Returns:
            Dict[str, Any]: Registration result
            
        Raises:
            UserAlreadyExistsException: If user already exists
            WeakPasswordException: If password is weak
        """
        await self._validate_password_strength(register_data.password)
        
        hashed_password = self._hash_password(register_data.password)
        
        user_data = {
            "email": register_data.email,
            "full_name": register_data.full_name,
            "hashed_password": hashed_password,
            "timezone": register_data.timezone,
            "language": register_data.language,
            "is_active": True,
            "email_verified": False
        }
        
        user = await self.user_repo.create_user(user_data)
        
        otp = await self._generate_otp(
            user_id=user.id,
            otp_type="email_verification",
            expires_in_minutes=60
        )
        
        return {
            "user_id": user.id,
            "email": user.email,
            "verification_code": otp.code,
            "message": "Registration successful. Please verify your email."
        }
    
    async def login_user(
        self, 
        login_data: LoginRequest,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authenticate user login.
        
        Args:
            login_data: Login request data
            ip_address: Client IP address
            user_agent: Client user agent
            
        Returns:
            Dict[str, Any]: Login result with tokens
            
        Raises:
            InvalidCredentialsException: If credentials are invalid
            InactiveUserException: If user is inactive
            TwoFactorRequiredException: If 2FA is required
        """
        user = await self.user_repo.get_by_email(login_data.email)
        if not user:
            raise InvalidCredentialsException()
        
        if not user.is_active:
            raise InactiveUserException(user_id=user.id)
        
        if not self._verify_password(login_data.password, user.hashed_password):
            await self._handle_failed_login(user.id, ip_address)
            raise InvalidCredentialsException()
        
        if user.two_factor_enabled and not login_data.otp_code:
            otp = await self._generate_otp(
                user_id=user.id,
                otp_type="login",
                expires_in_minutes=5,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            raise TwoFactorRequiredException(otp_type="login")
        
        if user.two_factor_enabled and login_data.otp_code:
            await self._verify_otp(
                user_id=user.id,
                code=login_data.otp_code,
                otp_type="login"
            )
        
        device_trust = None
        if login_data.remember_device:
            device_trust = await self._create_or_update_device_trust(
                user_id=user.id,
                device_name=login_data.device_name,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        tokens = await self._generate_tokens(
            user=user,
            two_factor_verified=user.two_factor_enabled,
            device_trusted=device_trust is not None
        )
        
        await self.user_repo.update_last_login(user.id)
        
        return {
            **tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role,
                "email_verified": user.email_verified
            },
            "device_token": device_trust.device_token if device_trust else None,
            "requires_2fa": False,
            "device_trusted": device_trust is not None
        }
    
    async def verify_email(self, email: str, otp_code: str) -> Dict[str, Any]:
        """
        Verify user email with OTP.
        
        Args:
            email: User email
            otp_code: Verification code
            
        Returns:
            Dict[str, Any]: Verification result
        """
        user = await self.user_repo.get_by_email_or_raise(email)
        
        await self._verify_otp(
            user_id=user.id,
            code=otp_code,
            otp_type="email_verification"
        )
        
        user = await self.user_repo.verify_email(user.id)
        
        return {
            "message": "Email verified successfully",
            "email_verified": True
        }
    
    async def change_password(
        self, 
        user_id: int, 
        change_data: ChangePasswordRequest
    ) -> Dict[str, Any]:
        """
        Change user password.
        
        Args:
            user_id: User ID
            change_data: Password change data
            
        Returns:
            Dict[str, Any]: Change result
        """
        user = await self.user_repo.get_by_id_or_raise(user_id)
        
        if not self._verify_password(change_data.current_password, user.hashed_password):
            raise InvalidCredentialsException("Current password is incorrect")
        
        await self._validate_password_strength(change_data.new_password)
        
        if self._verify_password(change_data.new_password, user.hashed_password):
            raise SamePasswordException()
        
        new_hashed_password = self._hash_password(change_data.new_password)
        
        await self.user_repo.update_user(user_id, {
            "hashed_password": new_hashed_password
        })
        
        await self.user_repo.update_password_timestamp(user_id)
        
        await self.token_repo.revoke_all_user_devices(user_id)
        
        return {
            "message": "Password changed successfully"
        }
    
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """
        Request password reset.
        
        Args:
            email: User email
            
        Returns:
            Dict[str, Any]: Reset request result
        """
        user = await self.user_repo.get_by_email(email)
        
        if user and user.is_active:
            otp = await self._generate_otp(
                user_id=user.id,
                otp_type="password_reset",
                expires_in_minutes=30
            )
        
        return {
            "message": "If an account with this email exists, you will receive a password reset code."
        }
    
    async def reset_password(
        self, 
        email: str, 
        otp_code: str, 
        new_password: str
    ) -> Dict[str, Any]:
        """
        Reset password with OTP.
        
        Args:
            email: User email
            otp_code: Reset code
            new_password: New password
            
        Returns:
            Dict[str, Any]: Reset result
        """
        user = await self.user_repo.get_by_email_or_raise(email)
        
        await self._verify_otp(
            user_id=user.id,
            code=otp_code,
            otp_type="password_reset"
        )
        
        await self._validate_password_strength(new_password)
        
        new_hashed_password = self._hash_password(new_password)
        
        await self.user_repo.update_user(user.id, {
            "hashed_password": new_hashed_password
        })
        
        await self.user_repo.update_password_timestamp(user.id)
        
        await self.token_repo.revoke_all_user_devices(user.id)
        
        return {
            "message": "Password reset successfully"
        }
    
    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh access token.
        
        Args:
            refresh_token: JWT refresh token
            
        Returns:
            Dict[str, Any]: New tokens
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            
            user_id = payload.get("sub")
            token_type = payload.get("type")
            
            if not user_id or token_type != "refresh":
                raise InvalidCredentialsException("Invalid refresh token")
            
            user = await self.user_repo.get_by_id_or_raise(int(user_id))
            
            if not user.is_active:
                raise InactiveUserException(user_id=user.id)
            
            tokens = await self._generate_tokens(user)
            
            return tokens
            
        except jwt.ExpiredSignatureError:
            raise InvalidCredentialsException("Refresh token expired")
        except jwt.InvalidTokenError:
            raise InvalidCredentialsException("Invalid refresh token")
    
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt."""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
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
    
    async def _generate_otp(
        self,
        user_id: int,
        otp_type: str,
        expires_in_minutes: int = 15,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> OTP:
        """Generate OTP for user."""
        code = f"{secrets.randbelow(1000000):06d}"
        
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        
        otp_data = {
            "user_id": user_id,
            "code": code,
            "otp_type": otp_type,
            "expires_at": expires_at,
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        return await self.token_repo.create_otp(otp_data)
    
    async def _verify_otp(self, user_id: int, code: str, otp_type: str) -> OTP:
        """Verify OTP code."""
        otp = await self.token_repo.get_valid_otp(user_id, code, otp_type)
        
        if not otp:
            latest_otp = await self.token_repo.get_latest_otp(user_id, otp_type)
            if latest_otp and not latest_otp.is_used:
                await self.token_repo.increment_otp_attempts(latest_otp.id)
                
                if not latest_otp.is_attempt_allowed():
                    raise InvalidOTPException("Maximum attempts exceeded")
            
            raise InvalidOTPException()
        
        if not otp.is_valid:
            if otp.is_expired:
                raise OTPExpiredException()
            else:
                await self.token_repo.increment_otp_attempts(otp.id)
                raise InvalidOTPException(
                    attempts_remaining=otp.attempts_remaining - 1
                )
        
        await self.token_repo.mark_otp_as_used(otp.id)
        
        return otp
    
    async def _generate_tokens(
        self,
        user: User,
        two_factor_verified: bool = False,
        device_trusted: bool = False
    ) -> Dict[str, Any]:
        """Generate JWT tokens for user."""
        now = datetime.utcnow()
        
        access_payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
            "type": "access",
            "iat": now.timestamp(),
            "exp": (now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp(),
            "2fa_verified": two_factor_verified,
            "device_trusted": device_trusted
        }
        
        refresh_payload = {
            "sub": str(user.id),
            "type": "refresh",
            "iat": now.timestamp(),
            "exp": (now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)).timestamp()
        }
        
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    async def _create_or_update_device_trust(
        self,
        user_id: int,
        device_name: Optional[str],
        ip_address: Optional[str],
        user_agent: Optional[str]
    ) -> DeviceTrust:
        """Create or update device trust."""
        existing_device = await self.token_repo.find_similar_device(
            user_id, user_agent or "", ip_address or ""
        )
        
        if existing_device:
            await self.token_repo.update_device_last_used(existing_device.id)
            return existing_device
        
        device_token = f"dt_{secrets.token_urlsafe(32)}"
        expires_at = datetime.utcnow() + timedelta(days=30)
        
        device_data = {
            "user_id": user_id,
            "device_token": device_token,
            "device_name": device_name or "Unknown Device",
            "user_agent": user_agent,
            "ip_address": ip_address,
            "expires_at": expires_at
        }
        
        return await self.token_repo.create_device_trust(device_data)
    
    async def _handle_failed_login(self, user_id: int, ip_address: Optional[str]) -> None:
        """Handle failed login attempt."""
        pass