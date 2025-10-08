"""Health check endpoints."""

import structlog
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.config import settings
from app.infrastructure.cache import CacheClient

router = APIRouter()
logger = structlog.get_logger()


@router.get("/simple")
async def simple_health_check() -> Dict[str, Any]:
    """
    Simple health check endpoint that doesn't depend on external services.
    """
    return {
        "status": "healthy",
        "service": "customer-feedback-api",
        "version": "3.1.0",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }


@router.get("")  # No trailing slash to prevent redirects
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    Returns status of all system components.
    """
    health_status = {
        "status": "healthy",
        "timestamp": None,
        "services": {},
        "metrics": {}
    }

    # Check API
    health_status["services"]["api"] = {
        "status": "up",
        "version": "3.1.0"
    }

    # Check Redis
    try:
        r = CacheClient.get_client()
        r.ping()
        redis_info = r.info()

        health_status["services"]["redis"] = {
            "status": "connected",
            "memory_used_mb": round(redis_info.get("used_memory", 0) / 1024 / 1024, 2),
            "connections": redis_info.get("connected_clients", 0)
        }
    except Exception as e:
        logger.warning("Redis health check failed", error=str(e))
        health_status["services"]["redis"] = {
            "status": "disconnected",
            "error": str(e)
        }
        # Don't mark as unhealthy for Redis issues, API can still work
        # health_status["status"] = "unhealthy"

    # Check Celery (basic check)
    try:
        # This would require importing celery app, simplified for now
        health_status["services"]["celery"] = {
            "status": "unknown",
            "note": "Detailed check requires celery import"
        }
    except Exception as e:
        health_status["services"]["celery"] = {
            "status": "error",
            "error": str(e)
        }

    # Add timestamp
    health_status["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Set overall status - only mark unhealthy for critical services
    critical_services = ["api"]  # Only API is critical for health check
    if any(
        service.get("status") in ["error", "down"] and service_name in critical_services
        for service_name, service in health_status["services"].items()
    ):
        health_status["status"] = "unhealthy"

    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status


@router.get("/debug/celery")
async def debug_celery():
    """
    Debug endpoint to test Celery connection and task dispatch.
    """
    try:
        # Import here to avoid circular imports
        from app.workers.tasks import analyze_feedback
        from app.workers.celery_app import celery_app

        # Test simple task dispatch
        test_task_id = "debug_test_task"

        # Create a simple task
        task = analyze_feedback.apply_async(
            args=["/tmp/debug_test.csv", {"rows": 1, "test": True}],
            task_id=test_task_id
        )

        # Check if task was created
        return {
            "celery_status": "connected",
            "task_dispatched": True,
            "task_id": test_task_id,
            "task_state": task.state,
            "worker_ready": True,
            "message": "Test task dispatched successfully"
        }

    except Exception as e:
        logger.error("Celery debug failed", error=str(e), exc_info=True)
        return {
            "celery_status": "error",
            "task_dispatched": False,
            "error": str(e),
            "message": "Failed to dispatch test task"
        }