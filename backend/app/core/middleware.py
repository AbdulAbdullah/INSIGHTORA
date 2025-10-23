"""
Custom middleware for the FastAPI application
"""

import time
import uuid
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Start timer
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"Response {request_id}: {response.status_code} "
            f"in {process_time:.4f}s"
        )
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware to add security headers
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware (Redis-based implementation would be better for production)
    """
    
    def __init__(self, app, calls_per_minute: int = 60):
        super().__init__(app)
        self.calls_per_minute = calls_per_minute
        self.clients = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Clean old entries (older than 1 minute)
        cutoff_time = current_time - 60
        self.clients = {
            ip: timestamps for ip, timestamps in self.clients.items()
            if any(t > cutoff_time for t in timestamps)
        }
        
        # Get client's recent requests
        if client_ip not in self.clients:
            self.clients[client_ip] = []
        
        # Filter to last minute
        self.clients[client_ip] = [
            t for t in self.clients[client_ip] if t > cutoff_time
        ]
        
        # Check rate limit
        if len(self.clients[client_ip]) >= self.calls_per_minute:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Try again later."
            )
        
        # Add current request
        self.clients[client_ip].append(current_time)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.calls_per_minute - len(self.clients[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.calls_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + 60))
        
        return response


class DatabaseMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle database session management
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Database error in request {getattr(request.state, 'request_id', 'unknown')}: {e}")
            raise


class CacheMiddleware(BaseHTTPMiddleware):
    """
    Simple caching middleware for GET requests
    """
    
    def __init__(self, app, cache_ttl: int = 300):
        super().__init__(app)
        self.cache_ttl = cache_ttl
        self.cache = {}  # In production, use Redis
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only cache GET requests
        if request.method != "GET":
            return await call_next(request)
        
        # Generate cache key
        cache_key = f"{request.url}"
        current_time = time.time()
        
        # Check cache
        if cache_key in self.cache:
            cached_response, timestamp = self.cache[cache_key]
            
            # Check if cache is still valid
            if current_time - timestamp < self.cache_ttl:
                logger.debug(f"Cache hit for {cache_key}")
                
                # Create response from cache
                from fastapi import Response
                response = Response(
                    content=cached_response["content"],
                    status_code=cached_response["status_code"],
                    headers=cached_response["headers"]
                )
                response.headers["X-Cache"] = "HIT"
                return response
        
        # Process request
        response = await call_next(request)
        
        # Cache successful GET responses
        if response.status_code == 200:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Cache the response
            self.cache[cache_key] = (
                {
                    "content": body,
                    "status_code": response.status_code,
                    "headers": dict(response.headers)
                },
                current_time
            )
            
            # Create new response with cached body
            from fastapi import Response
            new_response = Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            new_response.headers["X-Cache"] = "MISS"
            return new_response
        
        response.headers["X-Cache"] = "SKIP"
        return response