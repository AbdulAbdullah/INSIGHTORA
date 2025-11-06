"""
Handles database connections using SQLAlchemy with async support.
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


Base = declarative_base()

metadata = MetaData()

engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None


def create_database_engines():
    """Create database engines with connection pooling."""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )
    
    async_engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=settings.DEBUG
    )
    
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )
    
    AsyncSessionLocal = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    logger.info("Database engines created successfully")


async def init_db():
    """Initialize database and create tables."""
    try:
        from app.modules.auth.models import User, OTP, DeviceTrust
        
        if async_engine is None:
            create_database_engines()
        
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def get_async_session() -> AsyncSession:
    """
    Dependency to get async database session.
    
    Yields:
        AsyncSession: Database session
    """
    if AsyncSessionLocal is None:
        create_database_engines()
    
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


def get_sync_session():
    """
    Dependency to get synchronous database session.
    
    Yields:
        Session: Database session
    """
    if SessionLocal is None:
        create_database_engines()
    
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        db.close()


async def check_database_connection() -> bool:
    """
    Check if database connection is healthy.
    
    Returns:
        bool: True if connection is healthy
    """
    try:
        if async_engine is None:
            create_database_engines()
        
        async with async_engine.begin() as conn:
            await conn.execute("SELECT 1")
        
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False


get_db = get_sync_session

create_database_engines()
