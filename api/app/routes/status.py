"""Task status endpoint."""

import json
from datetime import datetime
import structlog
import redis.exceptions
from fastapi import APIRouter, HTTPException, Path

from app.config import settings
from app.schemas.status import StatusResponse, StatusError
from app.schemas.base import TaskStatus

router = APIRouter()
logger = structlog.get_logger()

# Redis client
import redis
redis_client = redis.from_url(settings.REDIS_URL)


@router.get("/{task_id}", response_model=StatusResponse)
async def get_task_status(
    task_id: str = Path(..., description="Task ID from upload endpoint")
):
    """
    Get the current status of an analysis task.

    Args:
        task_id: The task ID returned from upload endpoint

    Returns:
        StatusResponse with current task status and progress

    Raises:
        404: If task not found
    """
    try:
        # Check Redis for task status
        status_key = f"task_status:{task_id}"
        status_data = redis_client.get(status_key)

        if not status_data:
            # Try to get from Celery result backend
            result_key = f"celery-task-meta-{task_id}"
            celery_result = redis_client.get(result_key)

            if not celery_result:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "Task not found",
                        "details": "The task has expired or does not exist",
                        "code": "TASK_NOT_FOUND"
                    }
                )

            # Parse Celery result
            celery_data = json.loads(celery_result)
            status = _map_celery_status(celery_data.get("status", "PENDING"))

            # Check if results are available
            results_available = False
            if status == TaskStatus.COMPLETED:
                results_key = f"task_results:{task_id}"
                results_available = redis_client.exists(results_key) > 0

            return StatusResponse(
                task_id=task_id,
                status=status,
                progress=100 if status == TaskStatus.COMPLETED else 50,
                current_step="Processing" if status == TaskStatus.PROCESSING else None,
                results_available=results_available,
                messages=[]
            )

        # Parse status data
        status_info = json.loads(status_data)

        # Build response
        response = StatusResponse(
            task_id=task_id,
            status=TaskStatus(status_info.get("status", "queued")),
            progress=status_info.get("progress", 0),
            current_step=status_info.get("current_step"),
            messages=status_info.get("messages", [])
        )

        # Add timestamps
        if "started_at" in status_info:
            response.started_at = datetime.fromisoformat(status_info["started_at"])

        if status_info.get("status") == TaskStatus.COMPLETED.value:
            if "completed_at" in status_info:
                response.completed_at = datetime.fromisoformat(status_info["completed_at"])

            # Check if results exist
            results_key = f"task_results:{task_id}"
            response.results_available = redis_client.exists(results_key) > 0

            # Calculate duration
            if response.started_at and response.completed_at:
                duration = (response.completed_at - response.started_at).total_seconds()
                response.duration_seconds = duration

        elif status_info.get("status") == TaskStatus.FAILED.value:
            response.error = status_info.get("error", "Unknown error")
            response.details = status_info.get("details")
            if "failed_at" in status_info:
                response.failed_at = datetime.fromisoformat(status_info["failed_at"])
            response.retry_available = True

        # Estimate remaining time for processing tasks
        if response.status == TaskStatus.PROCESSING and response.progress > 0:
            # Simple estimation based on progress
            if response.started_at:
                elapsed = (datetime.utcnow() - response.started_at).total_seconds()
                if response.progress > 0:
                    total_estimated = elapsed / (response.progress / 100)
                    remaining = total_estimated - elapsed
                    response.estimated_remaining_seconds = max(0, int(remaining))

        logger.info(
            "Task status retrieved",
            task_id=task_id,
            status=response.status,
            progress=response.progress
        )

        return response

    except redis.exceptions.ConnectionError:
        logger.error("Redis connection failed")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service unavailable",
                "details": "Unable to connect to status service",
                "code": "SERVICE_UNAVAILABLE"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Error retrieving task status",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal error",
                "details": str(e),
                "code": "INTERNAL_ERROR"
            }
        )


def _map_celery_status(celery_status: str) -> TaskStatus:
    """Map Celery status to our TaskStatus enum."""
    status_map = {
        "PENDING": TaskStatus.QUEUED,
        "STARTED": TaskStatus.PROCESSING,
        "RETRY": TaskStatus.PROCESSING,
        "SUCCESS": TaskStatus.COMPLETED,
        "FAILURE": TaskStatus.FAILED,
        "REVOKED": TaskStatus.FAILED,
    }
    return status_map.get(celery_status, TaskStatus.QUEUED)