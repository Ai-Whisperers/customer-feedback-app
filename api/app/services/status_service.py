"""
Task status management service.
Handles task status updates and retrieval.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
import redis
import structlog

from app.schemas.base import TaskStatus
from app.config import settings

logger = structlog.get_logger()

# Redis client instance
redis_client = redis.from_url(settings.REDIS_URL)


def update_task_status(
    task_id: str,
    status: TaskStatus,
    progress: int = 0,
    message: str = "",
    error: Optional[str] = None
) -> None:
    """
    Update task status in Redis.

    Args:
        task_id: Task identifier
        status: Task status enum
        progress: Progress percentage (0-100)
        message: Status message
        error: Optional error message
    """
    status_data = {
        "task_id": task_id,
        "status": status.value,
        "progress": progress,
        "current_step": message,
        "updated_at": datetime.utcnow().isoformat(),
    }

    if error:
        status_data["error"] = error
        status_data["failed_at"] = datetime.utcnow().isoformat()

    try:
        redis_client.setex(
            f"task_status:{task_id}",
            settings.RESULTS_TTL_SECONDS,
            json.dumps(status_data)
        )

        logger.info(
            "Task status updated",
            task_id=task_id,
            status=status.value,
            progress=progress
        )

    except Exception as e:
        logger.error(
            "Failed to update task status",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        raise


def get_task_status(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Get task status from Redis.

    Args:
        task_id: Task identifier

    Returns:
        Task status dictionary or None if not found
    """
    try:
        status_json = redis_client.get(f"task_status:{task_id}")

        if status_json:
            return json.loads(status_json)

        return None

    except Exception as e:
        logger.error(
            "Failed to get task status",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        return None


def mark_task_started(task_id: str) -> None:
    """
    Mark a task as started.

    Args:
        task_id: Task identifier
    """
    update_task_status(
        task_id=task_id,
        status=TaskStatus.PROCESSING,
        progress=0,
        message="Iniciando análisis del archivo"
    )


def mark_task_completed(task_id: str) -> None:
    """
    Mark a task as completed.

    Args:
        task_id: Task identifier
    """
    update_task_status(
        task_id=task_id,
        status=TaskStatus.COMPLETED,
        progress=100,
        message="Análisis completado"
    )


def mark_task_failed(task_id: str, error_message: str) -> None:
    """
    Mark a task as failed.

    Args:
        task_id: Task identifier
        error_message: Error description
    """
    update_task_status(
        task_id=task_id,
        status=TaskStatus.FAILED,
        progress=0,
        error=error_message
    )


def update_task_progress(task_id: str, progress: int, message: str) -> None:
    """
    Update task progress.

    Args:
        task_id: Task identifier
        progress: Progress percentage (0-100)
        message: Progress message
    """
    update_task_status(
        task_id=task_id,
        status=TaskStatus.PROCESSING,
        progress=progress,
        message=message
    )