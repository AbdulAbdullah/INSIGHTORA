"""
Token Service

Business logic for token management including OTP generation,
device trust management, and token lifecycle operations.
"""

from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import secrets
import string

from ..repositories import TokenRepository, UserRepository
from ..models import OTP, DeviceTrust, User
from ..schemas.token import OTPCreate, DeviceTrustCreate
from ..exceptions import (
    InvalidOTPException, OTPExpiredException, OTPAttemptsExceededException,
    UserNotFoundException
)


class TokenService:
    """Service for token management operations."""
    
    def __init__(self, db: Session):
        """
        Initialize token service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.token_repo = TokenRepository(db)
        self.user_repo = UserRepository(db)
    
    
    async def generate_otp(self, otp_data: OTPCreate) -> Dict[str, Any]:
        """
        Generate a new OTP for user.
        
        Args:
            otp_data: OTP creation data
            
        Returns:
            Dict[str, Any]: OTP generation result
            
        Raises:
            UserNotFoundException: If user not found
        """
        user = await self.user_repo.get_by_id_or_raise(otp_data.user_id)
        
        code = self._generate_otp_code()
        
        expires_at = datetime.utcnow() + timedelta(minutes=otp_data.expires_in_minutes)
        
        otp_create_data = {
            "user_id": otp_data.user_id,
            "code": code,
            "otp_type": otp_data.otp_type.value,
            "expires_at": expires_at,
            "max_attempts": otp_data.max_attempts,
            "ip_address": otp_data.ip_address,
            "user_agent": otp_data.user_agent
        }
        
        otp = await self.token_repo.create_otp(otp_create_data)
        
        return {
            "otp_id": otp.id,
            "code": otp.code,
            "expires_at": otp.expires_at,
            "expires_in_minutes": otp_data.expires_in_minutes,
            "max_attempts": otp.max_attempts,
            "message": f"OTP generated for {otp_data.otp_type.value}"
        }
    
    async def verify_otp(
        self, 
        user_id: int, 
        code: str, 
        otp_type: str,
        ip_address: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Verify OTP code.
        
        Args:
            user_id: User ID
            code: OTP code to verify
            otp_type: Type of OTP
            ip_address: Client IP address
            
        Returns:
            Dict[str, Any]: Verification result
            
        Raises:
            InvalidOTPException: If OTP is invalid
            OTPExpiredException: If OTP is expired
            OTPAttemptsExceededException: If attempts exceeded
        """
        otp = await self.token_repo.get_valid_otp(user_id, code, otp_type)
        
        if not otp:
            latest_otp = await self.token_repo.get_latest_otp(user_id, otp_type)
            
            if latest_otp and not latest_otp.is_used:
                await self.token_repo.increment_otp_attempts(latest_otp.id)
                
                if latest_otp.attempts >= latest_otp.max_attempts - 1:
                    raise OTPAttemptsExceededException(max_attempts=latest_otp.max_attempts)
                
                raise InvalidOTPException(
                    attempts_remaining=latest_otp.max_attempts - latest_otp.attempts - 1
                )
            
            raise InvalidOTPException()
        
        if not otp.is_valid:
            if otp.is_expired:
                raise OTPExpiredException()
            
            await self.token_repo.increment_otp_attempts(otp.id)
            
            if otp.attempts >= otp.max_attempts - 1:
                raise OTPAttemptsExceededException(max_attempts=otp.max_attempts)
            
            raise InvalidOTPException(attempts_remaining=otp.attempts_remaining - 1)
        
        await self.token_repo.mark_otp_as_used(otp.id)
        
        return {
            "verified": True,
            "otp_id": otp.id,
            "otp_type": otp.otp_type,
            "message": "OTP verified successfully"
        }
    
    async def get_user_otps(
        self, 
        user_id: int, 
        otp_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get user's OTP history.
        
        Args:
            user_id: User ID
            otp_type: Optional OTP type filter
            limit: Maximum number of OTPs to return
            
        Returns:
            List[Dict[str, Any]]: List of user's OTPs
        """
        otps = await self.token_repo.get_user_otps(user_id, otp_type, limit)
        
        return [
            {
                "id": otp.id,
                "otp_type": otp.otp_type,
                "is_used": otp.is_used,
                "attempts": otp.attempts,
                "max_attempts": otp.max_attempts,
                "created_at": otp.created_at,
                "expires_at": otp.expires_at,
                "used_at": otp.used_at,
                "is_expired": otp.is_expired,
                "is_valid": otp.is_valid
            }
            for otp in otps
        ]
    
    async def cleanup_expired_otps(self) -> Dict[str, Any]:
        """
        Clean up expired OTPs.
        
        Returns:
            Dict[str, Any]: Cleanup result
        """
        deleted_count = await self.token_repo.cleanup_expired_otps()
        
        return {
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} expired OTPs"
        }
    
    
    async def create_device_trust(self, device_data: DeviceTrustCreate) -> Dict[str, Any]:
        """
        Create device trust for user.
        
        Args:
            device_data: Device trust creation data
            
        Returns:
            Dict[str, Any]: Device trust creation result
        """
        user = await self.user_repo.get_by_id_or_raise(device_data.user_id)
        
        existing_device = await self.token_repo.find_similar_device(
            device_data.user_id,
            device_data.user_agent or "",
            device_data.ip_address or ""
        )
        
        if existing_device:
            await self.token_repo.update_device_last_used(existing_device.id)
            
            return {
                "device_id": existing_device.id,
                "device_token": existing_device.device_token,
                "device_name": existing_device.device_name,
                "is_new": False,
                "expires_at": existing_device.expires_at,
                "message": "Existing device trust updated"
            }
        
        device_token = f"dt_{secrets.token_urlsafe(32)}"
        
        expires_at = datetime.utcnow() + timedelta(days=device_data.expires_in_days)
        
        browser, os = self._parse_user_agent(device_data.user_agent or "")
        
        device_create_data = {
            "user_id": device_data.user_id,
            "device_token": device_token,
            "device_name": device_data.device_name or "Unknown Device",
            "user_agent": device_data.user_agent,
            "ip_address": device_data.ip_address,
            "browser": browser,
            "os": os,
            "expires_at": expires_at
        }
        
        device_trust = await self.token_repo.create_device_trust(device_create_data)
        
        return {
            "device_id": device_trust.id,
            "device_token": device_trust.device_token,
            "device_name": device_trust.device_name,
            "is_new": True,
            "expires_at": device_trust.expires_at,
            "expires_in_days": device_data.expires_in_days,
            "message": "Device trust created successfully"
        }
    
    async def get_user_devices(self, user_id: int, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get user's trusted devices.
        
        Args:
            user_id: User ID
            active_only: Whether to return only active devices
            
        Returns:
            List[Dict[str, Any]]: List of user's devices
        """
        devices = await self.token_repo.get_user_device_trusts(user_id, active_only)
        
        return [
            {
                "id": device.id,
                "device_name": device.device_name,
                "browser": device.browser,
                "os": device.os,
                "ip_address": device.ip_address,
                "is_active": device.is_active,
                "created_at": device.created_at,
                "last_used_at": device.last_used_at,
                "expires_at": device.expires_at,
                "is_expired": device.is_expired,
                "is_valid": device.is_valid,
                "days_until_expiry": device.days_until_expiry
            }
            for device in devices
        ]
    
    async def revoke_device_trust(self, device_id: int, user_id: int) -> Dict[str, Any]:
        """
        Revoke device trust.
        
        Args:
            device_id: Device trust ID
            user_id: User ID (for authorization)
            
        Returns:
            Dict[str, Any]: Revocation result
        """
        device = await self.token_repo.get_device_trust_by_id(device_id)
        
        if not device or device.user_id != user_id:
            raise InvalidOTPException("Device not found or access denied")
        
        await self.token_repo.revoke_device_trust(device_id)
        
        return {
            "device_id": device_id,
            "revoked": True,
            "message": "Device trust revoked successfully"
        }
    
    async def revoke_all_user_devices(self, user_id: int) -> Dict[str, Any]:
        """
        Revoke all device trusts for user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict[str, Any]: Revocation result
        """
        revoked_count = await self.token_repo.revoke_all_user_devices(user_id)
        
        return {
            "user_id": user_id,
            "revoked_count": revoked_count,
            "message": f"Revoked {revoked_count} device trusts"
        }
    
    async def extend_device_trust(
        self, 
        device_id: int, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Extend device trust expiration.
        
        Args:
            device_id: Device trust ID
            user_id: User ID (for authorization)
            days: Number of days to extend
            
        Returns:
            Dict[str, Any]: Extension result
        """
        device = await self.token_repo.get_device_trust_by_id(device_id)
        
        if not device or device.user_id != user_id:
            raise InvalidOTPException("Device not found or access denied")
        
        updated_device = await self.token_repo.extend_device_trust(device_id, days)
        
        return {
            "device_id": device_id,
            "extended_days": days,
            "new_expires_at": updated_device.expires_at,
            "message": f"Device trust extended by {days} days"
        }
    
    async def cleanup_expired_devices(self) -> Dict[str, Any]:
        """
        Clean up expired device trusts.
        
        Returns:
            Dict[str, Any]: Cleanup result
        """
        deleted_count = await self.token_repo.cleanup_expired_device_trusts()
        
        return {
            "deleted_count": deleted_count,
            "message": f"Cleaned up {deleted_count} expired device trusts"
        }
    
    async def get_token_statistics(self) -> Dict[str, Any]:
        """
        Get token statistics.
        
        Returns:
            Dict[str, Any]: Token statistics
        """
        stats = await self.token_repo.get_token_statistics()
        
        return {
            "otps": {
                "total": stats["total_otps"],
                "active": stats["active_otps"]
            },
            "device_trusts": {
                "total": stats["total_devices"],
                "active": stats["active_devices"]
            }
        }
    
    
    def _generate_otp_code(self, length: int = 6) -> str:
        """Generate random OTP code."""
        return f"{secrets.randbelow(10**length):0{length}d}"
    
    def _parse_user_agent(self, user_agent: str) -> tuple[str, str]:
        """
        Parse user agent string to extract browser and OS.
        
        Args:
            user_agent: User agent string
            
        Returns:
            tuple[str, str]: Browser and OS names
        """
        browser = "Unknown"
        os = "Unknown"
        
        user_agent_lower = user_agent.lower()
        
        if "chrome" in user_agent_lower:
            browser = "Chrome"
        elif "firefox" in user_agent_lower:
            browser = "Firefox"
        elif "safari" in user_agent_lower:
            browser = "Safari"
        elif "edge" in user_agent_lower:
            browser = "Edge"
        
        if "windows" in user_agent_lower:
            os = "Windows"
        elif "mac" in user_agent_lower or "darwin" in user_agent_lower:
            os = "macOS"
        elif "linux" in user_agent_lower:
            os = "Linux"
        elif "android" in user_agent_lower:
            os = "Android"
        elif "ios" in user_agent_lower or "iphone" in user_agent_lower:
            os = "iOS"
        
        return browser, os