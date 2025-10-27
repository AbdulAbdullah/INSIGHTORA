"""
Rate Limiting Middleware and Utilities
"""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from typing import Optional
import logging

# Try to import Redis, make it optional
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

from .config import settings

logger = logging.getLogger(__name__)


def get_client_ip(request: Request) -> str:
    """
    Get client IP address from request, considering proxy headers
    """
    # Check for forwarded headers (common in production behind proxies)
    forwarded_ips = request.headers.get("X-Forwarded-For")
    if forwarded_ips:
        # Take the first IP (client IP) from the chain
        return forwarded_ips.split(",")[0].strip()
    
    # Check for other common proxy headers
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    # Fall back to direct connection IP
    client_host = getattr(request.client, "host", None)
    return client_host or "unknown"


def get_user_id_or_ip(request: Request) -> str:
    """
    Get user identifier for rate limiting (user ID if authenticated, otherwise IP)
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)
    if user and hasattr(user, "id"):
        return f"user:{user.id}"
    
    # Fall back to IP address
    return f"ip:{get_client_ip(request)}"


# Initialize Redis connection for rate limiting storage
redis_client = None
if REDIS_AVAILABLE:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        # Test connection
        redis_client.ping()
        logger.info("Redis connected successfully for rate limiting")
    except Exception as e:
        logger.warning(f"Redis connection failed, using in-memory rate limiting: {e}")
        redis_client = None
else:
    logger.warning("Redis not available, using in-memory rate limiting")


# Create rate limiter instance
limiter = Limiter(
    key_func=get_user_id_or_ip,
    storage_uri=settings.REDIS_URL if redis_client else None,
    default_limits=["1000/day", "100/hour"]  # Default global limits
)


async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """
    Custom handler for rate limit exceeded errors
    """
    detail = f"Rate limit exceeded: {exc.detail}"
    
    # Log the rate limit violation
    client_id = get_user_id_or_ip(request)
    logger.warning(f"Rate limit exceeded for {client_id}: {exc.detail}")
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "message": "Too many requests. Please try again later.",
            "detail": detail,
            "retry_after": exc.retry_after
        },
        headers={"Retry-After": str(exc.retry_after)}
    )


class AuthRateLimiter:
    """
    Specialized rate limiter for authentication endpoints
    """
    
    def __init__(self):
        self.redis = redis_client
    
    async def check_otp_attempts(self, email: str) -> bool:
        """
        Check if user has exceeded OTP attempt limits
        Returns True if user can attempt, False if rate limited
        """
        if not self.redis:
            return True  # Allow if Redis is not available
        
        try:
            key = f"otp_attempts:{email}"
            attempts = self.redis.get(key)
            
            if attempts is None:
                # First attempt
                self.redis.setex(key, 900, 1)  # 15 minutes expiry
                return True
            
            attempts = int(attempts)
            if attempts >= 3:
                # Too many attempts
                ttl = self.redis.ttl(key)
                logger.warning(f"OTP rate limit exceeded for {email}, TTL: {ttl}s")
                return False
            
            # Increment attempts
            self.redis.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Redis error checking OTP attempts: {e}")
            return True  # Allow on error
    
    async def check_login_attempts(self, email: str) -> bool:
        """
        Check if user has exceeded login attempt limits
        Returns True if user can attempt, False if rate limited
        """
        if not self.redis:
            return True
        
        try:
            key = f"login_attempts:{email}"
            attempts = self.redis.get(key)
            
            if attempts is None:
                # First attempt
                self.redis.setex(key, 3600, 1)  # 1 hour expiry
                return True
            
            attempts = int(attempts)
            if attempts >= 5:
                # Too many login attempts
                ttl = self.redis.ttl(key)
                logger.warning(f"Login rate limit exceeded for {email}, TTL: {ttl}s")
                return False
            
            # Increment attempts
            self.redis.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Redis error checking login attempts: {e}")
            return True
    
    async def reset_otp_attempts(self, email: str):
        """
        Reset OTP attempts for successful verification
        """
        if self.redis:
            try:
                self.redis.delete(f"otp_attempts:{email}")
            except Exception as e:
                logger.error(f"Redis error resetting OTP attempts: {e}")
    
    async def reset_login_attempts(self, email: str):
        """
        Reset login attempts for successful login
        """
        if self.redis:
            try:
                self.redis.delete(f"login_attempts:{email}")
            except Exception as e:
                logger.error(f"Redis error resetting login attempts: {e}")
    
    async def get_attempt_info(self, email: str, attempt_type: str) -> dict:
        """
        Get information about current attempt limits
        """
        if not self.redis:
            return {"attempts": 0, "max_attempts": 5, "ttl": 0}
        
        try:
            key = f"{attempt_type}_attempts:{email}"
            attempts = self.redis.get(key)
            ttl = self.redis.ttl(key) if attempts else 0
            
            max_attempts = 3 if attempt_type == "otp" else 5
            
            return {
                "attempts": int(attempts) if attempts else 0,
                "max_attempts": max_attempts,
                "ttl": ttl,
                "blocked": int(attempts) >= max_attempts if attempts else False
            }
            
        except Exception as e:
            logger.error(f"Redis error getting attempt info: {e}")
            return {"attempts": 0, "max_attempts": 5, "ttl": 0, "blocked": False}


# Global rate limiter instance
auth_rate_limiter = AuthRateLimiter()


# Rate limiting decorators for different endpoints
def auth_rate_limit(rate: str = "5/minute"):
    """Rate limiting decorator for auth endpoints"""
    return limiter.limit(rate)


def otp_rate_limit(rate: str = "3/15minutes"):
    """Rate limiting decorator for OTP endpoints"""
    return limiter.limit(rate)


def general_rate_limit(rate: str = "60/minute"):
    """Rate limiting decorator for general endpoints"""
    return limiter.limit(rate)