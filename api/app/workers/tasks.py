"""
Celery tasks for feedback analysis.
Entry point for async processing tasks.
"""

import asyncio
import time
import base64
import json
import tempfile
import os
from typing import Dict, List, Any
from celery import group
import structlog
import redis

from app.config import settings
from app.workers.celery_app import celery_app
from app.adapters.openai import openai_analyzer
from app.schemas.base import Language, TaskStatus
from app.utils.event_loop_monitor import monitor_event_loop, log_loop_state
from app.services import (
    analysis_service,
    status_service,
    storage_service
)
from app.utils.logging import log_task_start, log_task_complete, log_task_error
from app.utils.openai_logging import global_metrics

logger = structlog.get_logger()
redis_client = redis.from_url(settings.REDIS_URL)


@celery_app.task(bind=True, max_retries=3)
@monitor_event_loop("analyze_feedback_main_task")
def analyze_feedback(self, task_id_param: str, file_info: Dict[str, Any]) -> str:
    """
    Main task to analyze a feedback file.

    Args:
        task_id_param: Task ID (also used to retrieve file from Redis)
        file_info: Metadata about the file

    Returns:
        Task ID for result retrieval
    """
    task_id = self.request.id
    start_time = time.time()

    log_task_start("analyze_feedback", task_id, task_id_param=task_id_param)

    # Create a temporary file to work with
    temp_file = None

    try:
        # Initialize task
        status_service.mark_task_started(task_id)

        # Retrieve file from Redis
        status_service.update_task_progress(task_id, 5, "Recuperando archivo")
        file_key = f"file_content:{task_id_param}"
        file_data_str = redis_client.get(file_key)

        if not file_data_str:
            raise FileNotFoundError(f"File not found in Redis: {file_key}")

        # Parse file data
        file_data = eval(file_data_str)  # Safe since we control the data format
        content = base64.b64decode(file_data['content'])
        extension = file_data['extension']

        # Create temporary file
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as tmp:
            tmp.write(content)
            temp_file = tmp.name

        logger.info(
            "File retrieved from Redis and saved to temp",
            task_id=task_id,
            temp_file=temp_file,
            size_bytes=len(content)
        )

        # Load and validate file
        status_service.update_task_progress(task_id, 10, "Cargando archivo")
        df = analysis_service.load_and_validate_file(temp_file)

        # Prepare data with deduplication
        status_service.update_task_progress(task_id, 20, "Normalizando y deduplicando datos")
        comments, ratings, language_hint, dedup_info = analysis_service.prepare_analysis_data(df)

        # Create batches
        # Show deduplication savings
        original_count = dedup_info['original_count']
        filtered_count = dedup_info['filtered_count']
        savings_pct = round((1 - filtered_count/original_count) * 100, 1)

        status_service.update_task_progress(
            task_id, 30,
            f"Procesando {filtered_count} comentarios únicos de {original_count} (ahorro: {savings_pct}%)"
        )
        batches = openai_analyzer.optimize_batch_size(comments)

        logger.info("Created batches", task_id=task_id, batch_count=len(batches))

        # Process batches in parallel
        status_service.update_task_progress(
            task_id, 40,
            f"Procesando {len(batches)} lotes en paralelo (max {settings.CELERY_WORKER_CONCURRENCY} simultáneos)"
        )

        # Create and execute batch tasks in parallel
        batch_tasks = group(
            analyze_batch.s(batch, idx, language_hint)
            for idx, batch in enumerate(batches)
        )
        batch_results = batch_tasks.apply_async()

        # Monitor progress without blocking
        status_service.update_task_progress(task_id, 50, f"Procesando {len(batches)} lotes...")

        # Improved progress monitoring with detailed logging
        import time as time_module
        max_wait = 180  # 3 minutes max
        poll_interval = 1  # Check more frequently
        elapsed = 0
        last_ready_count = 0
        failed_batches = []

        while elapsed < max_wait:
            if batch_results.ready():
                break

            # Check how many tasks are complete and failed
            completed_count = 0
            for idx, result in enumerate(batch_results.results):
                if result.ready():
                    completed_count += 1
                    # Check if failed
                    if result.failed() and idx not in failed_batches:
                        failed_batches.append(idx)
                        logger.warning(
                            "Batch failed during processing",
                            batch_index=idx,
                            total_batches=len(batches)
                        )

            # Update progress based on actual completion
            if completed_count > last_ready_count:
                last_ready_count = completed_count
                progress_pct = 50 + int(40 * completed_count / len(batches))
                status_service.update_task_progress(
                    task_id, progress_pct,
                    f"Completados {completed_count}/{len(batches)} lotes (fallos: {len(failed_batches)})"
                )

            time_module.sleep(poll_interval)
            elapsed += poll_interval

        if not batch_results.ready():
            # Try to get partial results and log summary
            completed_count = sum(1 for result in batch_results.results if result.ready())

            # Log detailed timeout info
            logger.warning(
                "Batch processing timeout",
                task_id=task_id,
                completed=completed_count,
                total=len(batches),
                failed_batches=failed_batches,
                timeout_after_seconds=elapsed
            )

            # Log OpenAI metrics summary
            if hasattr(global_metrics, 'log_batch_summary'):
                global_metrics.log_batch_summary(
                    total_batches=len(batches),
                    completed_batches=completed_count,
                    failed_batches=failed_batches
                )

            raise TimeoutError(f"Batch processing timeout: {completed_count}/{len(batches)} completed")

        # Now safely get the results without using .join() or .get()
        status_service.update_task_progress(task_id, 90, "Consolidando resultados")

        # Collect results using non-blocking approach
        batch_analysis_results = []

        # Use Celery's collect() method which doesn't block
        from celery.result import allow_join_result

        with allow_join_result():
            # This context manager allows safe result collection
            for i, result in enumerate(batch_results.results):
                if result.successful():
                    try:
                        # Get the actual result data
                        batch_data = result.get(disable_sync_subtasks=False, timeout=1)
                        batch_analysis_results.append(batch_data)
                    except Exception as e:
                        logger.error(
                            "Failed to get batch result",
                            task_id=task_id,
                            batch_index=i,
                            error=str(e)
                        )
                        # Continue with other results
                elif result.failed():
                    error_info = str(result.info) if result.info else "Unknown error"
                    logger.error(
                        "Batch failed in final collection",
                        task_id=task_id,
                        batch_index=i,
                        error=error_info,
                        traceback=result.traceback if hasattr(result, 'traceback') else None
                    )

        final_results = analysis_service.merge_batch_results(
            batch_analysis_results, df, task_id, start_time,
            model_used=settings.AI_MODEL,
            dedup_info=dedup_info
        )

        # Store results
        status_service.update_task_progress(task_id, 95, "Guardando resultados")
        storage_service.store_analysis_results(task_id, final_results)

        # Complete with final metrics
        duration = time.time() - start_time

        # Log final OpenAI metrics
        if hasattr(global_metrics, 'log_batch_summary'):
            successful_count = len(batch_analysis_results)
            global_metrics.log_batch_summary(
                total_batches=len(batches),
                completed_batches=successful_count,
                failed_batches=list(set(range(len(batches))) - set(range(successful_count)))
            )

        status_service.mark_task_completed(task_id)
        log_task_complete("analyze_feedback", task_id, duration)

        # Clean up Redis file data on success
        try:
            redis_client.delete(f"file_content:{task_id_param}")
            logger.info("Redis file cleaned up on success", key=f"file_content:{task_id_param}")
        except Exception:
            pass  # Non-critical, Redis has TTL

        return task_id

    except Exception as e:
        _handle_task_error(self, task_id, str(e), start_time)
        raise

    finally:
        # Clean up temporary file
        if temp_file and os.path.exists(temp_file):
            try:
                os.remove(temp_file)
                logger.info("Temporary file cleaned up", file=temp_file)
            except Exception as cleanup_error:
                logger.warning("Failed to clean up temp file", error=str(cleanup_error))

        # Only delete Redis file on success (not on retry)
        # Redis TTL will handle cleanup for failed tasks
        # This ensures retries can still access the file


@celery_app.task(bind=True, max_retries=2, default_retry_delay=5)
@monitor_event_loop("analyze_batch_subtask")
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

        # Log event loop state before creating new loop
        log_loop_state("Before creating new event loop", batch_index=batch_index)

        # Run async analysis
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        log_loop_state("After creating new event loop",
                      batch_index=batch_index,
                      loop_id=id(loop))

        try:
            result = loop.run_until_complete(
                openai_analyzer.analyze_batch(comments, batch_index, lang_hint)
            )
            return result
        finally:
            log_loop_state("Before closing event loop", batch_index=batch_index)
            loop.close()
            log_loop_state("After closing event loop", batch_index=batch_index)

    except Exception as e:
        logger.error(
            "Batch analysis failed",
            task_id=task_id,
            batch_index=batch_index,
            error=str(e),
            retry_count=self.request.retries
        )
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 5 * (2 ** self.request.retries)  # 5, 10 seconds
            logger.info(
                "Retrying batch analysis",
                batch_index=batch_index,
                retry_in=retry_delay
            )
            raise self.retry(countdown=retry_delay)
        raise


# Function removed - monitoring now done inline in analyze_feedback


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