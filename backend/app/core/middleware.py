"""
Reusable Middleware Components

Custom middleware for logging, security, and performance monitoring.
"""

import time
import logging
from typing import Callable
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Process request and log details."""
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            process_time = time.time() - start_time
            
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"in {process_time:.3f}s"
            )
            
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request {request_id} failed after {process_time:.3f}s: {e}"
            )
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        if settings.SECURE_SSL_REDIRECT:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""
    
    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.requests = {}
        self.window_size = 60
        self.max_requests = settings.RATE_LIMIT_PER_MINUTE
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Apply rate limiting based on client IP."""
        client_ip = request.client.host if request.client else "unknown"
        
        if request.url.path in ["/health", "/docs", "/redoc"]:
            return await call_next(request)
        
        current_time = time.time()
        
        self.requests = {
            ip: timestamps for ip, timestamps in self.requests.items()
            if any(ts > current_time - self.window_size for ts in timestamps)
        }
        
        if client_ip in self.requests:
            recent_requests = [
                ts for ts in self.requests[client_ip]
                if ts > current_time - self.window_size
            ]
            
            if len(recent_requests) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {client_ip}")
                return Response(
                    content="Rate limit exceeded",
                    status_code=429,
                    headers={"Retry-After": "60"}
                )
            
            self.requests[client_ip] = recent_requests + [current_time]
        else:
            self.requests[client_ip] = [current_time]
        
        return await call_next(request)


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for global error handling."""
    
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        """Handle uncaught exceptions."""
        try:
            return await call_next(request)
        except Exception as e:
            request_id = getattr(request.state, 'request_id', 'unknown')
            
            logger.error(
                f"Unhandled exception in request {request_id}: {e}",
                exc_info=True
            )
            
            return Response(
                content="Internal server error",
                status_code=500,
                headers={"X-Request-ID": request_id}
            )


def setup_middleware(app: FastAPI) -> None:
    """
    Setup all middleware components.
    
    Args:
        app: FastAPI application instance
    """
    
    app.add_middleware(ErrorHandlingMiddleware)
    
    app.add_middleware(SecurityHeadersMiddleware)
    
    if settings.ENVIRONMENT == "production":
        app.add_middleware(RateLimitMiddleware)
    
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middleware setup completed")
