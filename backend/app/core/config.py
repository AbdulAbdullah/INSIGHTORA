"""
Application Configuration Settings
"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional
import os
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application
    APP_NAME: str = "Smart BI Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security - Load from environment variables
    SECRET_KEY: str = "dev-secret-key-change-in-production"  # Default for development
    REFRESH_SECRET_KEY: str = "dev-refresh-secret-change-in-production"  # Default for development
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS - Matching TypeScript app origins
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000", 
        "https://your-frontend-domain.com"
    ]
    
    # Database - Matching TypeScript app PostgreSQL configuration
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bi_assistant_db"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_NAME: str = "bi_assistant_db"
    DB_TEST_NAME: str = "bi_assistant_test_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 30
    DATABASE_POOL_TIMEOUT: int = 30
    
    # Redis (Caching and Celery)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_CACHE_TTL: int = 3600  # 1 hour
    
    # Celery (Background Tasks)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "uploads"
    ALLOWED_FILE_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls", ".json", ".parquet"]
    
    # AI and ML - Load from environment variables
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    CURRENT_PROVIDER: str = "groq"
    OPENAI_API_KEY: str = ""
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    
    # Email (for notifications) - Load from environment variables
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "noreply@notarize.com"
    EMAIL_FROM_NAME: str = "INSIGHTORA API Service"
    EMAIL_SECURE: bool = False
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        if not v or v == "":
            raise ValueError("DATABASE_URL must be provided")
        return v
    
    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def validate_secret_key(cls, v):
        if not v or len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env file


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()


# Database Configuration
def get_database_config():
    """
    Get database configuration for SQLAlchemy
    """
    return {
        "url": settings.DATABASE_URL,
        "pool_size": settings.DATABASE_POOL_SIZE,
        "max_overflow": settings.DATABASE_MAX_OVERFLOW,
        "pool_timeout": settings.DATABASE_POOL_TIMEOUT,
        "pool_recycle": 3600,  # 1 hour
        "echo": settings.DEBUG,
    }


# Redis Configuration  
def get_redis_config():
    """
    Get Redis configuration
    """
    from urllib.parse import urlparse
    
    parsed = urlparse(settings.REDIS_URL)
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 6379,
        "db": int(parsed.path[1:]) if parsed.path else 0,
        "password": parsed.password,
        "decode_responses": True,
        "socket_timeout": 5,
        "socket_connect_timeout": 5,
    }


# Celery Configuration
def get_celery_config():
    """
    Get Celery configuration
    """
    return {
        "broker_url": settings.CELERY_BROKER_URL,
        "result_backend": settings.CELERY_RESULT_BACKEND,
        "task_serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "timezone": "UTC",
        "enable_utc": True,
        "task_track_started": True,
        "task_time_limit": 300,  # 5 minutes
        "task_soft_time_limit": 240,  # 4 minutes
        "worker_prefetch_multiplier": 1,
        "task_acks_late": True,
    }