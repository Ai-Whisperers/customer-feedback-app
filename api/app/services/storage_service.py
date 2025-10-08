"""
Storage service for results persistence.
Handles storing and retrieving analysis results from Redis.
"""

import json
from typing import Optional, Dict, Any
import structlog

from app.config import settings
from app.infrastructure.cache import CacheClient

logger = structlog.get_logger()

# Redis client instance
redis_client = CacheClient.get_client()


def store_analysis_results(task_id: str, results: Dict[str, Any]) -> None:
    """
    Store analysis results in Redis.

    Args:
        task_id: Task identifier
        results: Analysis results dictionary

    Raises:
        Exception: If storage fails
    """
    try:
        results_json = json.dumps(results, ensure_ascii=False, default=str)

        redis_client.setex(
            f"task_results:{task_id}",
            settings.RESULTS_TTL_SECONDS,
            results_json
        )

        logger.info(
            "Results stored successfully",
            task_id=task_id,
            results_size_kb=len(results_json) / 1024
        )

    except Exception as e:
        logger.error(
            "Failed to store results",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        raise


def get_analysis_results(task_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve analysis results from Redis.

    Args:
        task_id: Task identifier

    Returns:
        Analysis results dictionary or None if not found
    """
    try:
        results_json = redis_client.get(f"task_results:{task_id}")

        if results_json:
            return json.loads(results_json)

        logger.warning("No results found for task", task_id=task_id)
        return None

    except Exception as e:
        logger.error(
            "Failed to retrieve results",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        return None


def delete_task_data(task_id: str) -> bool:
    """
    Delete task data from Redis.

    Args:
        task_id: Task identifier

    Returns:
        True if deletion was successful
    """
    try:
        # Delete both status and results
        status_key = f"task_status:{task_id}"
        results_key = f"task_results:{task_id}"

        deleted_count = redis_client.delete(status_key, results_key)

        logger.info(
            "Task data deleted",
            task_id=task_id,
            deleted_keys=deleted_count
        )

        return deleted_count > 0

    except Exception as e:
        logger.error(
            "Failed to delete task data",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        return False


def check_task_exists(task_id: str) -> bool:
    """
    Check if a task exists in storage.

    Args:
        task_id: Task identifier

    Returns:
        True if task exists
    """
    try:
        status_exists = redis_client.exists(f"task_status:{task_id}")
        results_exists = redis_client.exists(f"task_results:{task_id}")

        return bool(status_exists or results_exists)

    except Exception as e:
        logger.error(
            "Failed to check task existence",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        return False


def get_storage_info() -> Dict[str, Any]:
    """
    Get storage statistics.

    Returns:
        Dictionary with storage statistics
    """
    try:
        info = redis_client.info('memory')

        return {
            "used_memory": info.get('used_memory_human', 'N/A'),
            "used_memory_peak": info.get('used_memory_peak_human', 'N/A'),
            "total_keys": redis_client.dbsize()
        }

    except Exception as e:
        logger.error(
            "Failed to get storage info",
            error=str(e),
            exc_info=True
        )
        return {
            "used_memory": "N/A",
            "used_memory_peak": "N/A",
            "total_keys": 0
        }