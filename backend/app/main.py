"""
FastAPI Application Configuration
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
import logging
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import async_engine, Base, get_db
from app.core.middleware import LoggingMiddleware, SecurityMiddleware
from app.core.rate_limiter import limiter, rate_limit_exceeded_handler
from app.modules.auth.routes import router as auth_router
from app.modules.auth.exceptions import AuthenticationError
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events
    """
    # Startup
    logger.info("🚀 Starting Smart BI Platform Backend...")
    
    # Create database tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Database tables created/verified")
    logger.info("🎯 Application startup complete!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Smart BI Platform Backend...")
    await async_engine.dispose()
    logger.info("✅ Application shutdown complete!")


# Create FastAPI application
app = FastAPI(
    title="Smart BI Platform API",
    description="""
    ## Smart BI Platform API - Auth Module 🚀
    
    **Phase 1: Authentication & User Management**
    
    Currently implemented:
    * **🔐 User Registration**: Secure account creation with email verification
    * **� Two-Factor Authentication**: OTP-based login security
    * **�️ JWT Tokens**: Access and refresh token management
    * **📱 Device Trust**: Remember trusted devices for seamless access
    * **� Password Security**: Strong password requirements and hashing
    
    ### Authentication Features
    
    * Email-based OTP verification for registration and login
    * JWT access tokens with refresh token rotation
    * Device fingerprinting and trust management
    * Account lockout protection after failed attempts
    * Professional email templates for OTP delivery
    
    **Coming Next**: Data Sources, Analytics, and Visualizations modules
    """,
    version="1.0.0",
    contact={
        "name": "Abdul Abdullah",
        "email": "abdul@example.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(SecurityMiddleware)

# Rate Limiting Middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Trusted Host Middleware (production security)
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Custom Logging Middleware
app.add_middleware(LoggingMiddleware)


# Exception Handlers
@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle authentication errors"""
    return JSONResponse(
        status_code=401,
        content={
            "error": "Authentication Error",
            "message": str(exc),
            "type": "auth_error"
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "type": "http_error"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "type": "server_error"
        }
    )


# Include API Routers
app.include_router(
    auth_router,
    prefix="/api/v1",
    tags=["Authentication"]
)


# Root Endpoints
@app.get("/", tags=["Root"])
async def read_root():
    """
    Welcome endpoint with API information
    """
    return {
        "message": "🚀 Smart BI Platform API - Auth Module",
        "version": "1.0.0",
        "status": "running",
        "current_phase": "Phase 1 - Authentication & User Management",
        "features": [
            "🔐 User Registration with Email Verification",
            "🔑 Two-Factor Authentication (OTP)",
            "🛡️ JWT Token Management",
            "📱 Device Trust & Fingerprinting",
            "🔒 Password Security & Account Protection"
        ],
        "endpoints": {
            "auth": "/api/v1/auth"
        },
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint for monitoring
    """
    try:
        # Test database connection
        from app.core.database import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": time.time(),
        "services": {
            "database": db_status,
            "api": "healthy"
        },
        "version": "1.0.0"
    }


@app.get("/api/v1/info", tags=["Info"])
async def api_info():
    """
    API information and capabilities
    """
    return {
        "name": "Smart BI Platform API - Auth Module",
        "version": "1.0.0", 
        "environment": settings.ENVIRONMENT,
        "current_phase": "Phase 1 - Authentication & User Management",
        "implemented_features": {
            "authentication": "JWT-based with OTP verification",
            "registration": "Email verification with strong password requirements",
            "security": "Device trust, account lockout, rate limiting",
            "tokens": "Access/refresh tokens with automatic rotation"
        },
        "coming_next": {
            "data_sources": "PostgreSQL, MySQL, CSV, Excel connectivity",
            "analytics": "Natural language to SQL with LangChain",
            "visualizations": "Interactive charts with plotly",
            "dashboards": "Drag-and-drop dashboard builder"
        },
        "endpoints": {
            "auth": "/api/v1/auth"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=["app"],
        log_level="info"
    )