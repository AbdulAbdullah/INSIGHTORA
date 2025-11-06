"""
Token Repository

Data access layer for OTP and DeviceTrust model operations.
Handles all database interactions for token management.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta

from ..models import OTP, DeviceTrust, User
from ..exceptions import InvalidOTPException, OTPExpiredException


class TokenRepository:
    """Repository for token-related database operations."""
    
    def __init__(self, db: Session):
        """
        Initialize token repository.
        
        Args:
            db: Database session
        """
        self.db = db
    
    
    async def create_otp(self, otp_data: Dict[str, Any]) -> OTP:
        """
        Create a new OTP.
        
        Args:
            otp_data: OTP creation data
            
        Returns:
            OTP: Created OTP object
        """
        otp = OTP(**otp_data)
        self.db.add(otp)
        self.db.commit()
        self.db.refresh(otp)
        
        return otp
    
    async def get_otp_by_id(self, otp_id: int) -> Optional[OTP]:
        """
        Get OTP by ID.
        
        Args:
            otp_id: OTP ID
            
        Returns:
            Optional[OTP]: OTP object if found
        """
        return self.db.query(OTP).filter(OTP.id == otp_id).first()
    
    async def get_valid_otp(
        self, 
        user_id: int, 
        code: str, 
        otp_type: str
    ) -> Optional[OTP]:
        """
        Get valid OTP for user, code, and type.
        
        Args:
            user_id: User ID
            code: OTP code
            otp_type: OTP type
            
        Returns:
            Optional[OTP]: Valid OTP if found
        """
        return (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.user_id == user_id,
                    OTP.code == code,
                    OTP.otp_type == otp_type,
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow()
                )
            )
            .first()
        )
    
    async def get_latest_otp(
        self, 
        user_id: int, 
        otp_type: str
    ) -> Optional[OTP]:
        """
        Get latest OTP for user and type.
        
        Args:
            user_id: User ID
            otp_type: OTP type
            
        Returns:
            Optional[OTP]: Latest OTP if found
        """
        return (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.user_id == user_id,
                    OTP.otp_type == otp_type
                )
            )
            .order_by(desc(OTP.created_at))
            .first()
        )
    
    async def mark_otp_as_used(self, otp_id: int) -> OTP:
        """
        Mark OTP as used.
        
        Args:
            otp_id: OTP ID
            
        Returns:
            OTP: Updated OTP object
        """
        otp = self.db.query(OTP).filter(OTP.id == otp_id).first()
        if otp:
            otp.mark_as_used()
            self.db.commit()
            self.db.refresh(otp)
        
        return otp
    
    async def increment_otp_attempts(self, otp_id: int) -> OTP:
        """
        Increment OTP attempt counter.
        
        Args:
            otp_id: OTP ID
            
        Returns:
            OTP: Updated OTP object
        """
        otp = self.db.query(OTP).filter(OTP.id == otp_id).first()
        if otp:
            otp.increment_attempts()
            self.db.commit()
            self.db.refresh(otp)
        
        return otp
    
    async def cleanup_expired_otps(self) -> int:
        """
        Delete expired OTPs.
        
        Returns:
            int: Number of deleted OTPs
        """
        expired_otps = (
            self.db.query(OTP)
            .filter(OTP.expires_at <= datetime.utcnow())
        )
        
        count = expired_otps.count()
        expired_otps.delete()
        self.db.commit()
        
        return count
    
    async def cleanup_old_otps(self, days_old: int = 30) -> int:
        """
        Delete old OTPs (used or expired).
        
        Args:
            days_old: Number of days to keep OTPs
            
        Returns:
            int: Number of deleted OTPs
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        old_otps = (
            self.db.query(OTP)
            .filter(
                or_(
                    OTP.created_at <= cutoff_date,
                    and_(
                        OTP.is_used == True,
                        OTP.used_at <= cutoff_date
                    )
                )
            )
        )
        
        count = old_otps.count()
        old_otps.delete()
        self.db.commit()
        
        return count
    
    async def get_user_otps(
        self, 
        user_id: int, 
        otp_type: Optional[str] = None,
        limit: int = 10
    ) -> List[OTP]:
        """
        Get user's OTPs.
        
        Args:
            user_id: User ID
            otp_type: Optional OTP type filter
            limit: Maximum number of OTPs to return
            
        Returns:
            List[OTP]: List of user's OTPs
        """
        query = self.db.query(OTP).filter(OTP.user_id == user_id)
        
        if otp_type:
            query = query.filter(OTP.otp_type == otp_type)
        
        return (
            query
            .order_by(desc(OTP.created_at))
            .limit(limit)
            .all()
        )
    
    
    async def create_device_trust(self, device_data: Dict[str, Any]) -> DeviceTrust:
        """
        Create a new device trust.
        
        Args:
            device_data: Device trust creation data
            
        Returns:
            DeviceTrust: Created device trust object
        """
        device_trust = DeviceTrust(**device_data)
        self.db.add(device_trust)
        self.db.commit()
        self.db.refresh(device_trust)
        
        return device_trust
    
    async def get_device_trust_by_id(self, device_id: int) -> Optional[DeviceTrust]:
        """
        Get device trust by ID.
        
        Args:
            device_id: Device trust ID
            
        Returns:
            Optional[DeviceTrust]: Device trust object if found
        """
        return self.db.query(DeviceTrust).filter(DeviceTrust.id == device_id).first()
    
    async def get_device_trust_by_token(self, device_token: str) -> Optional[DeviceTrust]:
        """
        Get device trust by token.
        
        Args:
            device_token: Device trust token
            
        Returns:
            Optional[DeviceTrust]: Device trust object if found
        """
        return (
            self.db.query(DeviceTrust)
            .filter(DeviceTrust.device_token == device_token)
            .first()
        )
    
    async def get_user_device_trusts(
        self, 
        user_id: int, 
        active_only: bool = True
    ) -> List[DeviceTrust]:
        """
        Get user's device trusts.
        
        Args:
            user_id: User ID
            active_only: Whether to return only active devices
            
        Returns:
            List[DeviceTrust]: List of user's device trusts
        """
        query = self.db.query(DeviceTrust).filter(DeviceTrust.user_id == user_id)
        
        if active_only:
            query = query.filter(
                and_(
                    DeviceTrust.is_active == True,
                    DeviceTrust.expires_at > datetime.utcnow()
                )
            )
        
        return query.order_by(desc(DeviceTrust.last_used_at)).all()
    
    async def update_device_last_used(self, device_id: int) -> DeviceTrust:
        """
        Update device trust last used timestamp.
        
        Args:
            device_id: Device trust ID
            
        Returns:
            DeviceTrust: Updated device trust object
        """
        device = self.db.query(DeviceTrust).filter(DeviceTrust.id == device_id).first()
        if device:
            device.update_last_used()
            self.db.commit()
            self.db.refresh(device)
        
        return device
    
    async def revoke_device_trust(self, device_id: int) -> DeviceTrust:
        """
        Revoke device trust.
        
        Args:
            device_id: Device trust ID
            
        Returns:
            DeviceTrust: Updated device trust object
        """
        device = self.db.query(DeviceTrust).filter(DeviceTrust.id == device_id).first()
        if device:
            device.revoke()
            self.db.commit()
            self.db.refresh(device)
        
        return device
    
    async def extend_device_trust(self, device_id: int, days: int = 30) -> DeviceTrust:
        """
        Extend device trust expiration.
        
        Args:
            device_id: Device trust ID
            days: Number of days to extend
            
        Returns:
            DeviceTrust: Updated device trust object
        """
        device = self.db.query(DeviceTrust).filter(DeviceTrust.id == device_id).first()
        if device:
            device.extend_expiry(days)
            self.db.commit()
            self.db.refresh(device)
        
        return device
    
    async def cleanup_expired_device_trusts(self) -> int:
        """
        Delete expired device trusts.
        
        Returns:
            int: Number of deleted device trusts
        """
        expired_devices = (
            self.db.query(DeviceTrust)
            .filter(DeviceTrust.expires_at <= datetime.utcnow())
        )
        
        count = expired_devices.count()
        expired_devices.delete()
        self.db.commit()
        
        return count
    
    async def revoke_all_user_devices(self, user_id: int) -> int:
        """
        Revoke all device trusts for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            int: Number of revoked devices
        """
        devices = (
            self.db.query(DeviceTrust)
            .filter(
                and_(
                    DeviceTrust.user_id == user_id,
                    DeviceTrust.is_active == True
                )
            )
        )
        
        count = devices.count()
        devices.update({DeviceTrust.is_active: False})
        self.db.commit()
        
        return count
    
    async def find_similar_device(
        self, 
        user_id: int, 
        user_agent: str, 
        ip_address: str
    ) -> Optional[DeviceTrust]:
        """
        Find similar device trust for user.
        
        Args:
            user_id: User ID
            user_agent: User agent string
            ip_address: IP address
            
        Returns:
            Optional[DeviceTrust]: Similar device trust if found
        """
        return (
            self.db.query(DeviceTrust)
            .filter(
                and_(
                    DeviceTrust.user_id == user_id,
                    DeviceTrust.user_agent == user_agent,
                    DeviceTrust.ip_address == ip_address,
                    DeviceTrust.is_active == True,
                    DeviceTrust.expires_at > datetime.utcnow()
                )
            )
            .first()
        )
    
    async def get_token_statistics(self) -> Dict[str, Any]:
        """
        Get token statistics.
        
        Returns:
            Dict[str, Any]: Token statistics
        """
        total_otps = self.db.query(OTP).count()
        active_otps = (
            self.db.query(OTP)
            .filter(
                and_(
                    OTP.is_used == False,
                    OTP.expires_at > datetime.utcnow()
                )
            )
            .count()
        )
        
        total_devices = self.db.query(DeviceTrust).count()
        active_devices = (
            self.db.query(DeviceTrust)
            .filter(
                and_(
                    DeviceTrust.is_active == True,
                    DeviceTrust.expires_at > datetime.utcnow()
                )
            )
            .count()
        )
        
        return {
            "total_otps": total_otps,
            "active_otps": active_otps,
            "total_devices": total_devices,
            "active_devices": active_devices
        }