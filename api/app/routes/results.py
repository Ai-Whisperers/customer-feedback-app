"""Results retrieval endpoint."""

import json
import structlog
from fastapi import APIRouter, HTTPException, Path, Query
from typing import Optional

from app.config import settings
from app.schemas.analysis import AnalysisResults

router = APIRouter()
logger = structlog.get_logger()

# Redis client
import redis
redis_client = redis.from_url(settings.REDIS_URL)


@router.get("/{task_id}")
async def get_results(
    task_id: str = Path(..., description="Task ID from upload endpoint"),
    format: str = Query("json", pattern="^(json|summary)$", description="Response format"),
    include_rows: bool = Query(True, description="Include per-row analysis")
):
    """
    Get analysis results for a completed task.

    Args:
        task_id: The task ID returned from upload endpoint
        format: Response format (json or summary)
        include_rows: Whether to include detailed row analysis

    Returns:
        AnalysisResults with complete analysis data

    Raises:
        404: If results not found
    """
    try:
        # Get results from Redis
        results_key = f"task_results:{task_id}"
        results_data = redis_client.get(results_key)

        if not results_data:
            # Check if task exists but not completed
            status_key = f"task_status:{task_id}"
            status_data = redis_client.get(status_key)

            if status_data:
                status_info = json.loads(status_data)
                if status_info.get("status") != "completed":
                    raise HTTPException(
                        status_code=404,
                        detail={
                            "error": "Results not ready",
                            "details": f"Task is still {status_info.get('status')}",
                            "code": "RESULTS_NOT_READY"
                        }
                    )

            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Results not found",
                    "details": "Task results have expired or do not exist",
                    "code": "RESULTS_NOT_FOUND"
                }
            )

        # Parse results
        results = json.loads(results_data)

        # Apply format filters
        if format == "summary":
            # Return only summary without row details
            results.pop("rows", None)

        elif not include_rows:
            # Remove row details if not requested
            results.pop("rows", None)

        logger.info(
            "Results retrieved",
            task_id=task_id,
            format=format,
            include_rows=include_rows,
            total_comments=results.get("metadata", {}).get("total_comments", 0)
        )

        return results

    except redis.exceptions.ConnectionError:
        logger.error("Redis connection failed")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "Service unavailable",
                "details": "Unable to connect to results service",
                "code": "SERVICE_UNAVAILABLE"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Error retrieving results",
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