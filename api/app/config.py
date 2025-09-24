"""Application configuration using Pydantic Settings."""

import os
from pathlib import Path
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    # Try to find .env file, but don't fail if it doesn't exist
    # Environment variables always take precedence over .env file
    _env_file_path = Path(__file__).parent.parent.parent / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_env_file_path) if _env_file_path.exists() else None,
        env_file_encoding="utf-8",
        case_sensitive=True,
        # This ensures environment variables override .env file values
        env_ignore_empty=False,
        extra="ignore"  # Ignore extra environment variables
    )

    # Application
    APP_ENV: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    SECRET_KEY: str = Field(default="NtJIvemZxXOP5EBMMMagLf4VZglFrXlSoF5Bvz1Ub80", min_length=32)
    ALLOWED_ORIGINS: Optional[str] = Field(default=None)  # Not needed for private API
    PORT: int = Field(default=8000)

    # OpenAI Configuration
    OPENAI_API_KEY: str = Field(default="", min_length=0)  # Allow empty for health checks
    AI_MODEL: str = Field(default="gpt-4o-mini")  # Stable Chat Completions API
    OPENAI_TIMEOUT_SECONDS: int = Field(default=30, ge=10, le=120)

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/0")

    # File Processing
    FILE_MAX_MB: int = Field(default=20)
    MAX_BATCH_SIZE: int = Field(default=50)  # Optimized for token limits
    RESULTS_TTL_SECONDS: int = Field(default=86400)  # 24 hours

    # Rate Limiting
    MAX_RPS: int = Field(default=8)  # OpenAI rate limit

    # Hybrid Analysis Configuration (New)
    HYBRID_ANALYSIS_ENABLED: bool = Field(default=True)
    LOCAL_SENTIMENT_LIBRARY: str = Field(default="vader")
    SENTIMENT_CONFIDENCE_THRESHOLD: float = Field(default=0.05)

    # Memory Management (New)
    MEMORY_WARNING_MB: int = Field(default=400)
    MEMORY_CRITICAL_MB: int = Field(default=450)
    MIN_BATCH_SIZE: int = Field(default=10)
    DYNAMIC_BATCH_SIZING: bool = Field(default=True)

    # Parallel Processing Configuration
    OPENAI_CONCURRENT_WORKERS: int = Field(default=4, ge=1, le=10)
    BATCH_SIZE_OPTIMAL: int = Field(default=100, ge=50, le=200)
    ENABLE_PARALLEL_PROCESSING: bool = Field(default=True)  # Re-enabled with event loop fix!
    ENABLE_COMMENT_CACHE: bool = Field(default=True)
    CACHE_TTL_DAYS: int = Field(default=7, ge=1, le=30)

    # Performance Monitoring
    LOG_PERFORMANCE_METRICS: bool = Field(default=True)
    ALERT_THRESHOLD_SECONDS: int = Field(default=15)

    # Excel Export Formatting
    EXCEL_FORMATTING_ENABLED: bool = Field(default=True)
    EXCEL_ENABLE_CHARTS: bool = Field(default=True)
    EXCEL_ENABLE_CONDITIONAL: bool = Field(default=True)

    # Celery Worker Configuration
    CELERY_WORKER_CONCURRENCY: int = Field(default=4)  # Blueprint recommendation

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