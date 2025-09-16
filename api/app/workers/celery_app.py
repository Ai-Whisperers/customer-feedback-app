"""
Celery application configuration.
Handles async processing of feedback analysis tasks.
"""

from celery import Celery
from kombu import serialization
import structlog

from app.config import settings

# Setup logging for workers
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    context_class=dict,
    cache_logger_on_first_use=True,
)

# Create Celery app
celery_app = Celery(
    "feedback_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task routing
    task_routes={
        "app.workers.tasks.analyze_feedback": {"queue": "analysis"},
        "app.workers.tasks.analyze_batch": {"queue": "analysis"},
        "app.workers.tasks.merge_results": {"queue": "processing"},
    },

    # Task execution
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,

    # Results
    result_expires=settings.RESULTS_TTL_SECONDS,
    result_persistent=True,

    # Task limits
    task_time_limit=600,  # 10 minutes
    task_soft_time_limit=540,  # 9 minutes warning

    # Worker configuration
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",

    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,

    # Redis specific
    broker_transport_options={
        "visibility_timeout": 3600,  # 1 hour
        "fanout_prefix": True,
        "fanout_patterns": True
    },
    result_backend_transport_options={
        "master_name": "mymaster",
    },

    # Beat schedule (for future periodic tasks)
    beat_schedule={
        "cleanup-expired-tasks": {
            "task": "app.workers.tasks.cleanup_expired_tasks",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing."""
    logger = structlog.get_logger()
    logger.info("Debug task executed", task_id=self.request.id)
    return f"Request: {self.request!r}"


# Health check task
@celery_app.task
def health_check():
    """Health check task."""
    import redis

    # Check Redis connection
    try:
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "redis": f"error: {str(e)}"}


if __name__ == "__main__":
    celery_app.start()