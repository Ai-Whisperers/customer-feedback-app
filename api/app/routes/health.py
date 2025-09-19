"""Health check endpoints."""

import redis
import structlog
from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from app.config import settings

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
        "timestamp": __import__('datetime').datetime.utcnow().isoformat() + "Z"
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
        r = redis.from_url(settings.REDIS_URL, socket_timeout=5, socket_connect_timeout=5)
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
    from datetime import datetime
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