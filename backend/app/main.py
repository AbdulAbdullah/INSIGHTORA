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
from app.api import auth, data_sources, queries, dashboards
from app.utils.exceptions import BusinessLogicError, DataProcessingError

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
    ## Smart Business Intelligence Platform 🚀
    
    A powerful BI platform that transforms your data into actionable insights using:
    
    * **🤖 AI-Powered Queries**: Ask questions in natural language
    * **📊 Interactive Visualizations**: Beautiful charts and dashboards  
    * **🔗 Multi-Source Connectivity**: Connect to any database or file
    * **⚡ Real-time Analytics**: Live data streaming and updates
    * **🛡️ Enterprise Security**: JWT authentication and role-based access
    
    ### Features
    
    * Natural language to SQL conversion with LangChain
    * Interactive chart generation with plotly
    * Multi-database support (PostgreSQL, MySQL, SQL Server, Oracle)
    * File processing (CSV, Excel, JSON)
    * Background task processing with Celery
    * Real-time WebSocket updates
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
@app.exception_handler(BusinessLogicError)
async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
    """Handle business logic errors"""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Business Logic Error",
            "message": str(exc),
            "type": "business_error"
        }
    )


@app.exception_handler(DataProcessingError)
async def data_processing_error_handler(request: Request, exc: DataProcessingError):
    """Handle data processing errors"""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Data Processing Error",
            "message": str(exc),
            "type": "data_error"
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
    auth.router,
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

app.include_router(
    data_sources.router,
    prefix="/api/v1/data-sources",
    tags=["Data Sources"]
)

app.include_router(
    queries.router,
    prefix="/api/v1/queries",
    tags=["Queries"]
)

app.include_router(
    dashboards.router,
    prefix="/api/v1/dashboards",
    tags=["Dashboards"]
)


# Root Endpoints
@app.get("/", tags=["Root"])
async def read_root():
    """
    Welcome endpoint with API information
    """
    return {
        "message": "🚀 Smart BI Platform API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "AI-Powered Natural Language Queries",
            "Interactive Data Visualizations", 
            "Multi-Database Connectivity",
            "Real-time Analytics",
            "Enterprise Security"
        ],
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
        "name": "Smart BI Platform API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "authentication": "JWT-based with refresh tokens",
            "databases": ["PostgreSQL", "MySQL", "SQL Server", "Oracle", "MongoDB"],
            "file_formats": ["CSV", "Excel", "JSON", "Parquet"],
            "ai_models": ["LangChain", "Groq LLaMA", "OpenAI"],
            "visualizations": ["plotly", "matplotlib", "seaborn"],
            "background_tasks": "Celery with Redis"
        },
        "endpoints": {
            "auth": "/api/v1/auth",
            "data_sources": "/api/v1/data-sources", 
            "queries": "/api/v1/queries",
            "dashboards": "/api/v1/dashboards"
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