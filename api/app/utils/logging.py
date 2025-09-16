"""Structured logging configuration."""

import logging
import structlog
from typing import Any, Dict

from app.config import settings


def setup_logging() -> None:
    """Setup structured logging with JSON output."""

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        handlers=[logging.StreamHandler()]
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance."""
    return structlog.get_logger(name)


def log_task_start(task_name: str, task_id: str, **kwargs) -> None:
    """Log task start."""
    logger = get_logger()
    logger.info(
        "Task started",
        task_name=task_name,
        task_id=task_id,
        **kwargs
    )


def log_task_complete(task_name: str, task_id: str, duration: float, **kwargs) -> None:
    """Log task completion."""
    logger = get_logger()
    logger.info(
        "Task completed",
        task_name=task_name,
        task_id=task_id,
        duration_seconds=duration,
        **kwargs
    )


def log_task_error(task_name: str, task_id: str, error: str, **kwargs) -> None:
    """Log task error."""
    logger = get_logger()
    logger.error(
        "Task failed",
        task_name=task_name,
        task_id=task_id,
        error=error,
        **kwargs
    )