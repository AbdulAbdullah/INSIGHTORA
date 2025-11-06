"""
Application Lifecycle Events

Handles startup and shutdown events for the FastAPI application.
"""

import logging
from app.core.database import init_db, check_database_connection
from app.core.config import settings

logger = logging.getLogger(__name__)


async def startup_event():
    """
    Application startup event handler.
    
    Initializes database, connections, and other startup tasks.
    """
    logger.info("Starting Smart BI Platform API...")
    
    try:
        await init_db()
        logger.info("Database initialized successfully")
        
        db_healthy = await check_database_connection()
        if not db_healthy:
            logger.error("Database connection check failed")
            raise Exception("Database connection failed")
        
        
        
        
        logger.info(f"Smart BI Platform API started successfully on {settings.FASTAPI_HOST}:{settings.FASTAPI_PORT}")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise


async def shutdown_event():
    """
    Application shutdown event handler.
    
    Cleans up resources and connections.
    """
    logger.info("Shutting down Smart BI Platform API...")
    
    try:
        
        
        
        
        logger.info("Smart BI Platform API shutdown completed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}")
