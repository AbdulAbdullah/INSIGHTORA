"""
Centralized Configuration Management

Handles all application settings using Pydantic for validation.
"""

from typing import List, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with validation."""
    
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "0.0.0.0"]
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://your-frontend-domain.com"
    ]
    
    REDIS_URL: str = "redis://localhost:6379/0"
    
    MAX_FILE_SIZE_MB: int = 100
    UPLOAD_DIRECTORY: str = "./uploads"
    
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    CURRENT_PROVIDER: str = "groq"
    OPENAI_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    EMAIL_FROM: str = "noreply@insightora.com"
    EMAIL_FROM_NAME: str = "INSIGHTORA API Service"
    DEFAULT_FROM_NAME: str = "INSIGHTORA API Service"
    
    FASTAPI_HOST: str = "0.0.0.0"
    FASTAPI_PORT: int = 8000
    FASTAPI_RELOAD: bool = True
    
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    PANDAS_MAX_ROWS: int = 10000
    NUMPY_RANDOM_SEED: int = 42
    MATPLOTLIB_BACKEND: str = "Agg"
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    
    CACHE_TTL: int = 3600
    CACHE_MAX_SIZE: int = 1000
    
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    
    SECURE_SSL_REDIRECT: bool = False
    SECURE_PROXY_SSL_HEADER: bool = False
    
    @field_validator("ALLOWED_HOSTS", "ALLOWED_ORIGINS", "CELERY_ACCEPT_CONTENT", mode="before")
    @classmethod
    def parse_list_from_string(cls, v):
        """Parse list from string if needed."""
        if isinstance(v, str):
            import json
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [item.strip() for item in v.split(",")]
        return v
    
    @property
    def DATABASE_URL(self) -> str:
        """Construct database URL."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Construct async database URL."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def MAX_FILE_SIZE_BYTES(self) -> int:
        """Convert MB to bytes."""
        return self.MAX_FILE_SIZE_MB * 1024 * 1024
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }


settings = Settings()


def get_settings() -> Settings:
    """Get settings instance."""
    return settings


upload_path = Path(settings.UPLOAD_DIRECTORY)
upload_path.mkdir(parents=True, exist_ok=True)
