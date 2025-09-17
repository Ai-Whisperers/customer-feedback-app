"""
Celery tasks for feedback analysis.
Entry point for async processing tasks.
"""

import asyncio
import time
from typing import Dict, List, Any
from celery import group
import structlog

from app.workers.celery_app import celery_app
from app.adapters.openai_client import openai_analyzer
from app.schemas.base import Language, TaskStatus
from app.services import (
    analysis_service,
    status_service,
    storage_service
)
from app.utils.logging import log_task_start, log_task_complete, log_task_error

logger = structlog.get_logger()


@celery_app.task(bind=True, max_retries=3)
def analyze_feedback(self, file_path: str, file_info: Dict[str, Any]) -> str:
    """
    Main task to analyze a feedback file.

    Args:
        file_path: Path to the uploaded file
        file_info: Metadata about the file

    Returns:
        Task ID for result retrieval
    """
    task_id = self.request.id
    start_time = time.time()

    log_task_start("analyze_feedback", task_id, file_path=file_path)

    try:
        # Initialize task
        status_service.mark_task_started(task_id)

        # Load and validate file
        status_service.update_task_progress(task_id, 10, "Cargando archivo")
        df = analysis_service.load_and_validate_file(file_path)

        # Prepare data
        status_service.update_task_progress(task_id, 20, "Normalizando datos")
        comments, ratings, language_hint = analysis_service.prepare_analysis_data(df)

        # Create batches
        status_service.update_task_progress(
            task_id, 30,
            f"Creando lotes para {len(comments)} comentarios"
        )
        batches = openai_analyzer.optimize_batch_size(comments)

        logger.info("Created batches", task_id=task_id, batch_count=len(batches))

        # Process batches
        status_service.update_task_progress(
            task_id, 40,
            f"Procesando {len(batches)} lotes con IA"
        )

        # Create and execute batch tasks
        batch_tasks = group(
            analyze_batch.s(batch, idx, language_hint)
            for idx, batch in enumerate(batches)
        )
        batch_results = batch_tasks.apply_async()

        # Monitor progress
        _monitor_batch_progress(task_id, batch_results, len(batches))

        # Merge results
        status_service.update_task_progress(task_id, 90, "Consolidando resultados")
        batch_analysis_results = batch_results.get()

        final_results = analysis_service.merge_batch_results(
            batch_analysis_results, df, task_id, start_time
        )

        # Store results
        status_service.update_task_progress(task_id, 95, "Guardando resultados")
        storage_service.store_analysis_results(task_id, final_results)

        # Complete
        duration = time.time() - start_time
        status_service.mark_task_completed(task_id)
        log_task_complete("analyze_feedback", task_id, duration)

        return task_id

    except Exception as e:
        _handle_task_error(self, task_id, str(e), start_time)
        raise


@celery_app.task(bind=True)
def analyze_batch(
    self,
    comments: List[str],
    batch_index: int,
    language_hint: str = None
) -> Dict[str, Any]:
    """
    Analyze a single batch of comments.

    Args:
        comments: List of comments to analyze
        batch_index: Index of this batch
        language_hint: Optional language hint

    Returns:
        Analysis results for this batch
    """
    task_id = self.request.id

    logger.info(
        "Processing batch",
        task_id=task_id,
        batch_index=batch_index,
        comment_count=len(comments)
    )

    try:
        lang_hint = Language(language_hint) if language_hint else None

        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                openai_analyzer.analyze_batch(comments, batch_index, lang_hint)
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(
            "Batch analysis failed",
            task_id=task_id,
            batch_index=batch_index,
            error=str(e)
        )
        raise


def _monitor_batch_progress(task_id: str, batch_results: Any, total_batches: int):
    """Monitor batch processing progress."""
    completed_batches = 0
    while not batch_results.ready():
        time.sleep(2)
        current_completed = sum(1 for r in batch_results.results if r.ready())
        if current_completed > completed_batches:
            completed_batches = current_completed
            progress = 40 + int(50 * completed_batches / total_batches)
            status_service.update_task_progress(
                task_id, progress,
                f"Procesados {completed_batches}/{total_batches} lotes"
            )


def _handle_task_error(task_obj: Any, task_id: str, error: str, start_time: float):
    """Handle task error and retry logic."""
    duration = time.time() - start_time
    status_service.mark_task_failed(task_id, error)
    log_task_error("analyze_feedback", task_id, error)

    if task_obj.request.retries < task_obj.max_retries:
        logger.info(
            "Retrying task",
            task_id=task_id,
            retry_count=task_obj.request.retries + 1
        )
        raise task_obj.retry(countdown=60 * (task_obj.request.retries + 1))


@celery_app.task
def cleanup_expired_tasks() -> Dict[str, Any]:
    """
    Periodic task to clean up expired results from Redis.
    Runs every hour and removes tasks older than TTL.

    Returns:
        Statistics about the cleanup operation
    """
    import redis
    from datetime import datetime, timedelta
    from app.config import settings

    logger.info("Starting cleanup of expired tasks")

    try:
        # Connect to Redis
        r = redis.from_url(settings.REDIS_URL)

        # Get current time and expiry threshold
        now = datetime.utcnow()
        expiry_time = now - timedelta(seconds=settings.RESULTS_TTL_SECONDS)
        expiry_timestamp = expiry_time.timestamp()

        # Track statistics
        stats = {
            "checked": 0,
            "deleted": 0,
            "errors": 0,
            "start_time": now.isoformat(),
        }

        # Scan for task keys
        for key in r.scan_iter(match="celery-task-meta-*"):
            stats["checked"] += 1

            try:
                # Get task metadata
                task_data = r.get(key)
                if not task_data:
                    continue

                import json
                task_meta = json.loads(task_data)

                # Check if task is expired based on date_done
                if "date_done" in task_meta:
                    # Parse the date_done timestamp
                    task_timestamp = datetime.fromisoformat(
                        task_meta["date_done"].replace("Z", "+00:00")
                    ).timestamp()

                    # Delete if expired
                    if task_timestamp < expiry_timestamp:
                        r.delete(key)
                        stats["deleted"] += 1

                        # Also try to delete associated result data
                        result_key = key.replace("celery-task-meta-", "result-")
                        if r.exists(result_key):
                            r.delete(result_key)

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Error processing task key",
                    key=key.decode() if isinstance(key, bytes) else key,
                    error=str(e)
                )

        # Clean up orphaned result keys
        for key in r.scan_iter(match="result-*"):
            stats["checked"] += 1

            try:
                # Check TTL
                ttl = r.ttl(key)
                if ttl == -1:  # No TTL set
                    # Set a TTL to ensure cleanup
                    r.expire(key, settings.RESULTS_TTL_SECONDS)
                elif ttl == -2:  # Key doesn't exist
                    continue

            except Exception as e:
                stats["errors"] += 1
                logger.error(
                    "Error processing result key",
                    key=key.decode() if isinstance(key, bytes) else key,
                    error=str(e)
                )

        stats["end_time"] = datetime.utcnow().isoformat()
        stats["duration_seconds"] = (
            datetime.utcnow() - now
        ).total_seconds()

        logger.info(
            "Cleanup completed",
            checked=stats["checked"],
            deleted=stats["deleted"],
            errors=stats["errors"],
            duration=stats["duration_seconds"]
        )

        return stats

    except Exception as e:
        logger.error("Cleanup task failed", error=str(e))
        raise