"""Application configuration using Pydantic Settings."""

import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )

    # Application
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(min_length=32)
    ALLOWED_ORIGINS: List[str] = Field(default_factory=list)
    PORT: int = Field(default=8000)

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(min_length=1)
    AI_MODEL: str = Field(default="gpt-4o-mini")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # File Processing
    FILE_MAX_MB: int = Field(default=20)
    MAX_BATCH_SIZE: int = Field(default=50)
    RESULTS_TTL_SECONDS: int = Field(default=86400)  # 24 hours

    # Rate Limiting
    MAX_RPS: int = Field(default=8)

    # Celery Worker Configuration
    CELERY_WORKER_CONCURRENCY: int = Field(default=4)

    # Optional
    SENTRY_DSN: Optional[str] = Field(default=None)
    LOG_LEVEL: str = Field(default="INFO")
    DATABASE_URL: Optional[str] = Field(default=None)

    @property
    def file_max_bytes(self) -> int:
        """Convert MB to bytes."""
        return self.FILE_MAX_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.APP_ENV.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.APP_ENV.lower() == "development"


settings = Settings()