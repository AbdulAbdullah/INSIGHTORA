"""
Auth Module Services - Business logic for authentication
"""

import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import bcrypt
import logging

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_token_pair
from app.core.email_service import email_service
from .models import User, OTPVerification, RefreshToken, DeviceTrust
from .schemas import UserCreate, UserLogin, OTPVerify, DeviceTrustCreate
from .exceptions import (
    AuthenticationError,
    UserNotFoundError,
    InvalidOTPError,
    AccountLockedError,
    EmailNotVerifiedError
)

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service handling user registration, login, and session management
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.otp_service = OTPService(db)
    
    async def register_user(self, user_data: UserCreate, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new user and send verification OTP
        """
        try:
            # Check if user already exists
            existing_user = await self._get_user_by_email(user_data.email)
            if existing_user:
                if existing_user.is_verified:
                    raise AuthenticationError("User with this email already exists")
                else:
                    # User exists but not verified, allow re-registration
                    await self.db.delete(existing_user)
                    await self.db.commit()
            
            # Hash password
            hashed_password = self._hash_password(user_data.password)
            
            # Create user
            user = User(
                email=user_data.email,
                name=user_data.name,
                hashed_password=hashed_password,
                account_type=user_data.account_type,
                company=user_data.company,
                job_title=user_data.job_title,
                phone=user_data.phone,
                is_verified=False  # Require email verification
            )
            
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            
            # Generate and send registration OTP
            otp_code = await self.otp_service.generate_otp(
                user_id=user.id,
                otp_type="registration",
                context_data=request_info
            )
            
            # Send registration email
            await self._send_registration_email(user.email, user.name, otp_code)
            
            return {
                "message": "Registration successful. Please check your email for verification code.",
                "email_masked": self._mask_email(user.email),
                "expires_in": 600  # 10 minutes
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Registration error: {str(e)}")
            raise AuthenticationError(f"Registration failed: {str(e)}")
    
    async def verify_registration(self, otp_data: OTPVerify, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify registration OTP and activate user account
        """
        try:
            # Get user
            user = await self._get_user_by_email(otp_data.email)
            if not user:
                raise UserNotFoundError("User not found")
            
            # Verify OTP
            is_valid = await self.otp_service.verify_otp(
                user_id=user.id,
                otp_code=otp_data.otp_code,
                otp_type="registration"
            )
            
            if not is_valid:
                raise InvalidOTPError("Invalid or expired OTP code")
            
            # Activate user account
            user.is_verified = True
            user.is_active = True
            await self.db.commit()
            
            # Create device trust if requested
            device_trust = None
            if otp_data.remember_device:
                device_trust = await self._create_device_trust(
                    user_id=user.id,
                    device_name=otp_data.device_name or "Unknown Device",
                    request_info=request_info
                )
            
            # Generate JWT tokens
            access_token, refresh_token = await self._generate_tokens(user, request_info)
            
            # Send welcome email
            await self._send_welcome_email(user.email, user.name)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user.to_dict(),
                "device_trusted": device_trust is not None
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Registration verification error: {str(e)}")
            raise
    
    async def login_user(self, login_data: UserLogin, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Authenticate user and initiate login process
        """
        try:
            # Get user and validate
            user = await self._get_user_by_email(login_data.email)
            if not user:
                raise UserNotFoundError("Invalid email or password")
            
            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                raise AccountLockedError("Account is temporarily locked due to too many failed attempts")
            
            # Verify password
            if not self._verify_password(login_data.password, user.hashed_password):
                await self._handle_failed_login(user)
                raise AuthenticationError("Invalid email or password")
            
            # Check if account is verified
            if not user.is_verified:
                raise EmailNotVerifiedError("Please verify your email address before logging in")
            
            # Check if account is active
            if not user.is_active:
                raise AuthenticationError("Account is deactivated")
            
            # Reset failed login attempts
            user.login_attempts = 0
            user.locked_until = None
            
            # Check for trusted device
            device_fingerprint = self._generate_device_fingerprint(request_info)
            trusted_device = await self._get_trusted_device(user.id, device_fingerprint)
            
            if trusted_device and trusted_device.trust_expires_at > datetime.utcnow():
                # Trusted device - skip OTP
                user.last_login = datetime.utcnow()
                await self.db.commit()
                
                # Generate tokens
                access_token, refresh_token = await self._generate_tokens(user, request_info)
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "token_type": "bearer",
                    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    "user": user.to_dict(),
                    "trusted_device": True
                }
            else:
                # Generate and send login OTP
                otp_code = await self.otp_service.generate_otp(
                    user_id=user.id,
                    otp_type="login",
                    context_data=request_info
                )
                
                await self._send_login_email(user.email, user.name, otp_code)
                
                return {
                    "message": "Please check your email for login verification code.",
                    "email_masked": self._mask_email(user.email),
                    "expires_in": 600,  # 10 minutes
                    "requires_otp": True
                }
                
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Login error: {str(e)}")
            raise
    
    async def verify_login(self, otp_data: OTPVerify, request_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify login OTP and complete authentication
        """
        try:
            # Get user
            user = await self._get_user_by_email(otp_data.email)
            if not user:
                raise UserNotFoundError("User not found")
            
            # Verify OTP
            is_valid = await self.otp_service.verify_otp(
                user_id=user.id,
                otp_code=otp_data.otp_code,
                otp_type="login"
            )
            
            if not is_valid:
                raise InvalidOTPError("Invalid or expired OTP code")
            
            # Update last login
            user.last_login = datetime.utcnow()
            
            # Create device trust if requested
            device_trust = None
            if otp_data.remember_device:
                device_trust = await self._create_device_trust(
                    user_id=user.id,
                    device_name=otp_data.device_name or "Unknown Device",
                    request_info=request_info
                )
            
            await self.db.commit()
            
            # Generate JWT tokens
            access_token, refresh_token = await self._generate_tokens(user, request_info)
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user.to_dict(),
                "device_trusted": device_trust is not None
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Login verification error: {str(e)}")
            raise
    
    # Helper methods
    async def _get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _mask_email(self, email: str) -> str:
        """Mask email for privacy"""
        local, domain = email.split('@')
        if len(local) <= 2:
            masked_local = local[0] + '*' * (len(local) - 1)
        else:
            masked_local = local[:2] + '*' * (len(local) - 3) + local[-1]
        return f"{masked_local}@{domain}"
    
    async def _generate_tokens(self, user: User, request_info: Dict[str, Any]) -> Tuple[str, str]:
        """Generate JWT access and refresh tokens"""
        # Use core security function to create tokens
        token_pair = create_token_pair(
            user_id=user.id,
            email=user.email,
            scopes=["user"]  # Basic user scope
        )
        
        # Create refresh token record in database
        refresh_token = RefreshToken(
            user_id=user.id,
            token=token_pair.refresh_token,
            device_fingerprint=self._generate_device_fingerprint(request_info),
            device_name=request_info.get("device_name", "Unknown Device"),
            device_type=request_info.get("device_type", "desktop"),
            user_agent=request_info.get("user_agent"),
            ip_address=request_info.get("ip_address"),
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        self.db.add(refresh_token)
        await self.db.commit()
        
        return token_pair.access_token, token_pair.refresh_token
    
    def _generate_device_fingerprint(self, request_info: Dict[str, Any]) -> str:
        """Generate device fingerprint from request info"""
        fingerprint_data = (
            request_info.get("user_agent", "") +
            request_info.get("accept_language", "") +
            request_info.get("screen_resolution", "") +
            request_info.get("timezone", "")
        )
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    async def _send_registration_email(self, email: str, name: str, otp_code: str):
        """Send registration verification email"""
        try:
            success = await email_service.send_registration_otp(email, name, otp_code)
            if success:
                logger.info(f"Registration OTP email sent successfully to {email}")
            else:
                logger.error(f"Failed to send registration OTP email to {email}")
        except Exception as e:
            logger.error(f"Error sending registration email to {email}: {str(e)}")
            raise
    
    async def _send_login_email(self, email: str, name: str, otp_code: str):
        """Send login verification email"""
        try:
            success = await email_service.send_login_otp(email, name, otp_code)
            if success:
                logger.info(f"Login OTP email sent successfully to {email}")
            else:
                logger.error(f"Failed to send login OTP email to {email}")
        except Exception as e:
            logger.error(f"Error sending login email to {email}: {str(e)}")
            raise
    
    async def _send_welcome_email(self, email: str, name: str):
        """Send welcome email after successful registration"""
        try:
            success = await email_service.send_welcome_email(email, name)
            if success:
                logger.info(f"Welcome email sent successfully to {email}")
            else:
                logger.error(f"Failed to send welcome email to {email}")
        except Exception as e:
            logger.error(f"Error sending welcome email to {email}: {str(e)}")
            # Don't raise here as welcome email is not critical
    
    async def _handle_failed_login(self, user: User):
        """Handle failed login attempt"""
        user.login_attempts += 1
        
        # Lock account after 5 failed attempts
        if user.login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=15)
        
        await self.db.commit()
    
    async def _get_trusted_device(self, user_id: int, device_fingerprint: str) -> Optional[DeviceTrust]:
        """Get trusted device by fingerprint"""
        result = await self.db.execute(
            select(DeviceTrust)
            .where(DeviceTrust.user_id == user_id)
            .where(DeviceTrust.device_fingerprint == device_fingerprint)
            .where(DeviceTrust.is_active == True)
        )
        return result.scalar_one_or_none()
    
    async def _create_device_trust(self, user_id: int, device_name: str, request_info: Dict[str, Any]) -> DeviceTrust:
        """Create device trust record"""
        device_trust = DeviceTrust(
            user_id=user_id,
            device_fingerprint=self._generate_device_fingerprint(request_info),
            device_name=device_name,
            device_type=request_info.get("device_type", "desktop"),
            user_agent=request_info.get("user_agent"),
            ip_address=request_info.get("ip_address"),
            location=request_info.get("location", "Unknown"),
            trust_expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db.add(device_trust)
        await self.db.commit()
        await self.db.refresh(device_trust)
        
        return device_trust


class OTPService:
    """
    OTP (One-Time Password) service for two-factor authentication
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def generate_otp(self, user_id: int, otp_type: str, context_data: Dict[str, Any] = None) -> str:
        """
        Generate a new OTP for the user
        """
        # Invalidate any existing OTPs of the same type
        await self.db.execute(
            update(OTPVerification)
            .where(OTPVerification.user_id == user_id)
            .where(OTPVerification.otp_type == otp_type)
            .where(OTPVerification.is_used == False)
            .values(is_expired=True)
        )
        
        # Generate 6-digit OTP
        otp_code = str(secrets.randbelow(900000) + 100000)
        
        # Create OTP record
        otp = OTPVerification(
            user_id=user_id,
            otp_code=otp_code,
            otp_type=otp_type,
            expires_at=datetime.utcnow() + timedelta(minutes=10),  # 10 minutes expiry
            context_data=context_data or {}
        )
        
        self.db.add(otp)
        await self.db.commit()
        
        return otp_code
    
    async def verify_otp(self, user_id: int, otp_code: str, otp_type: str) -> bool:
        """
        Verify OTP code
        """
        # Get active OTP
        result = await self.db.execute(
            select(OTPVerification)
            .where(OTPVerification.user_id == user_id)
            .where(OTPVerification.otp_type == otp_type)
            .where(OTPVerification.is_used == False)
            .where(OTPVerification.is_expired == False)
            .where(OTPVerification.expires_at > datetime.utcnow())
        )
        otp = result.scalar_one_or_none()
        
        if not otp:
            return False
        
        # Check max attempts
        if otp.attempts >= otp.max_attempts:
            otp.is_expired = True
            await self.db.commit()
            return False
        
        # Increment attempts
        otp.attempts += 1
        
        # Verify code
        if otp.otp_code == otp_code:
            otp.is_used = True
            otp.used_at = datetime.utcnow()
            await self.db.commit()
            return True
        else:
            await self.db.commit()
            return False