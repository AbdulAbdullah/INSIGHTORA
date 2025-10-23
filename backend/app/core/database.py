"""
Database Configuration and Session Management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import asyncio
from typing import AsyncGenerator, Generator

from app.core.config import get_database_config

# Get database configuration
db_config = get_database_config()

# Create async engine for FastAPI
async_engine = create_async_engine(
    db_config["url"].replace("postgresql://", "postgresql+asyncpg://"),
    pool_size=db_config["pool_size"],
    max_overflow=db_config["max_overflow"],
    pool_timeout=db_config["pool_timeout"],
    pool_recycle=db_config["pool_recycle"],
    echo=db_config["echo"],
)

# Create sync engine for Alembic migrations and blocking operations
sync_engine = create_engine(
    db_config["url"],
    pool_size=db_config["pool_size"],
    max_overflow=db_config["max_overflow"],
    pool_timeout=db_config["pool_timeout"],
    pool_recycle=db_config["pool_recycle"],
    echo=db_config["echo"],
)

# Session makers
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()

# For backward compatibility (will be replaced by async_engine)
engine = sync_engine


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Async database session dependency for FastAPI
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db() -> Generator[SessionLocal, None, None]:
    """
    Sync database session dependency (for compatibility)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """
    Initialize database tables
    """
    async with async_engine.begin() as conn:
        # Import all models to ensure they're registered
        from app.models import user, data_source, dashboard, query
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Close database connections
    """
    await async_engine.dispose()


# Database health check
async def check_db_health() -> bool:
    """
    Check if database is healthy
    """
    try:
        async with AsyncSessionLocal() as session:
            await session.execute("SELECT 1")
            return True
    except Exception:
        return False