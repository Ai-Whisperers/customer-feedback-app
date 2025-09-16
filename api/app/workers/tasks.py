"""
Celery tasks for feedback analysis.
Main processing pipeline for analyzing customer feedback.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import structlog
from celery import group
import redis

from app.workers.celery_app import celery_app
from app.adapters.openai_client import openai_analyzer
from app.config import settings
from app.schemas.base import Language, TaskStatus
from app.utils.logging import log_task_start, log_task_complete, log_task_error

logger = structlog.get_logger()

# Redis client for status updates
redis_client = redis.from_url(settings.REDIS_URL)


def update_task_status(
    task_id: str,
    status: TaskStatus,
    progress: int = 0,
    message: str = "",
    error: Optional[str] = None
):
    """Update task status in Redis."""
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

    redis_client.setex(
        f"task_status:{task_id}",
        settings.RESULTS_TTL_SECONDS,
        json.dumps(status_data)
    )


@celery_app.task(bind=True, max_retries=3)
def analyze_feedback(self, file_path: str, file_info: Dict[str, Any]) -> str:
    """
    Main task to analyze a feedback file.
    Orchestrates the entire analysis pipeline.

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
        # Update status: Starting
        update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            0,
            "Iniciando análisis del archivo"
        )

        # Step 1: Load and validate file
        update_task_status(task_id, TaskStatus.PROCESSING, 10, "Cargando archivo")

        df = load_and_validate_file(file_path)
        if df.empty:
            raise ValueError("No valid data found in file")

        # Step 2: Normalize data
        update_task_status(task_id, TaskStatus.PROCESSING, 20, "Normalizando datos")

        df = normalize_feedback_data(df)
        comments = df['Comentario Final'].tolist()
        ratings = df['Nota'].tolist()

        # Step 3: Create batches
        update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            30,
            f"Creando lotes para {len(comments)} comentarios"
        )

        # Detect dominant language for hint
        language_hint = detect_dominant_language(comments[:10])

        # Optimize batching
        batches = openai_analyzer.optimize_batch_size(comments)

        logger.info(
            "Created analysis batches",
            task_id=task_id,
            total_comments=len(comments),
            total_batches=len(batches)
        )

        # Step 4: Process batches in parallel
        update_task_status(
            task_id,
            TaskStatus.PROCESSING,
            40,
            f"Procesando {len(batches)} lotes con IA"
        )

        # Create batch analysis tasks
        batch_tasks = group(
            analyze_batch.s(batch, idx, language_hint)
            for idx, batch in enumerate(batches)
        )

        # Execute batch analysis
        batch_results = batch_tasks.apply_async()

        # Wait for all batches with progress updates
        completed_batches = 0
        while not batch_results.ready():
            time.sleep(2)  # Poll every 2 seconds

            # Count completed batches
            current_completed = sum(1 for result in batch_results.results if result.ready())

            if current_completed > completed_batches:
                completed_batches = current_completed
                progress = 40 + int(50 * completed_batches / len(batches))
                update_task_status(
                    task_id,
                    TaskStatus.PROCESSING,
                    progress,
                    f"Procesados {completed_batches}/{len(batches)} lotes"
                )

        # Get all results
        batch_analysis_results = batch_results.get()

        # Step 5: Merge results
        update_task_status(task_id, TaskStatus.PROCESSING, 90, "Consolidando resultados")

        final_results = merge_batch_results(
            batch_analysis_results,
            df,
            task_id,
            start_time
        )

        # Step 6: Store final results
        update_task_status(task_id, TaskStatus.PROCESSING, 95, "Guardando resultados")

        store_analysis_results(task_id, final_results)

        # Complete task
        duration = time.time() - start_time
        update_task_status(task_id, TaskStatus.COMPLETED, 100, "Análisis completado")

        log_task_complete("analyze_feedback", task_id, duration)

        return task_id

    except Exception as e:
        duration = time.time() - start_time
        error_msg = str(e)

        update_task_status(task_id, TaskStatus.FAILED, 0, error=error_msg)
        log_task_error("analyze_feedback", task_id, error_msg)

        # Retry logic
        if self.request.retries < self.max_retries:
            logger.info(
                "Retrying failed task",
                task_id=task_id,
                retry_count=self.request.retries + 1,
                error=error_msg
            )
            raise self.retry(countdown=60 * (self.request.retries + 1))

        raise


@celery_app.task(bind=True)
def analyze_batch(self, comments: List[str], batch_index: int, language_hint: Optional[str] = None) -> Dict[str, Any]:
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
        "Starting batch analysis",
        task_id=task_id,
        batch_index=batch_index,
        comment_count=len(comments)
    )

    try:
        # Convert language hint
        lang_hint = Language(language_hint) if language_hint else None

        # Run async analysis in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(
                openai_analyzer.analyze_batch(
                    comments,
                    batch_index,
                    lang_hint
                )
            )
            return result
        finally:
            loop.close()

    except Exception as e:
        logger.error(
            "Batch analysis failed",
            task_id=task_id,
            batch_index=batch_index,
            error=str(e),
            exc_info=True
        )
        raise


def load_and_validate_file(file_path: str) -> pd.DataFrame:
    """Load and validate uploaded file."""
    try:
        # Determine file type and read
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:  # Excel files
            df = pd.read_excel(file_path)

        # Validate required columns
        required_columns = ['Nota', 'Comentario Final']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df

    except Exception as e:
        logger.error("File loading failed", file_path=file_path, error=str(e))
        raise


def normalize_feedback_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize and clean feedback data."""
    # Clean text
    df['Comentario Final'] = df['Comentario Final'].astype(str).str.strip()

    # Filter valid ratings
    df = df[(df['Nota'] >= 0) & (df['Nota'] <= 10)]

    # Filter valid comments (min 3 characters)
    df = df[df['Comentario Final'].str.len() >= 3]

    # Calculate NPS if not present
    if 'NPS' not in df.columns:
        df['NPS'] = df['Nota'].apply(calculate_nps_category)

    # Reset index
    df = df.reset_index(drop=True)

    return df


def calculate_nps_category(rating: int) -> str:
    """Calculate NPS category from rating."""
    if rating <= 6:
        return "detractor"
    elif rating <= 8:
        return "passive"
    else:
        return "promoter"


def detect_dominant_language(sample_comments: List[str]) -> Optional[str]:
    """Detect dominant language from sample comments."""
    spanish_indicators = ['ñ', 'á', 'é', 'í', 'ó', 'ú']
    spanish_words = ['el', 'la', 'de', 'que', 'en', 'por', 'un', 'con']

    spanish_score = 0
    total_comments = len(sample_comments)

    for comment in sample_comments:
        comment_lower = comment.lower()

        # Check for Spanish characters
        if any(char in comment_lower for char in spanish_indicators):
            spanish_score += 2

        # Check for Spanish words
        words = comment_lower.split()
        spanish_word_count = sum(1 for word in spanish_words if word in words)
        if spanish_word_count >= 2:
            spanish_score += 1

    # If >60% comments seem Spanish, return Spanish hint
    if spanish_score / total_comments > 0.6:
        return "es"
    else:
        return "en"


def merge_batch_results(
    batch_results: List[Dict[str, Any]],
    original_df: pd.DataFrame,
    task_id: str,
    start_time: float
) -> Dict[str, Any]:
    """Merge results from all batches into final results."""
    logger.info("Merging batch results", task_id=task_id, batch_count=len(batch_results))

    all_comments = []
    emotion_totals = {}
    pain_points_counter = {}
    sentiment_counts = {"muy_positivo": 0, "positivo": 0, "neutral": 0, "negativo": 0, "muy_negativo": 0}
    language_counts = {"es": 0, "en": 0}
    total_churn_risk = 0
    nps_counts = {"promoter": 0, "passive": 0, "detractor": 0}

    # Process each batch result
    for batch_result in batch_results:
        comments = batch_result.get("comments", [])
        all_comments.extend(comments)

        # Aggregate emotions
        for comment in comments:
            emotions = comment.get("emotions", {})
            for emotion, value in emotions.items():
                emotion_totals[emotion] = emotion_totals.get(emotion, 0) + value

            # Count sentiment
            sentiment = comment.get("sentiment", "neutral")
            sentiment_counts[sentiment] += 1

            # Count language
            language = comment.get("language", "es")
            language_counts[language] += 1

            # Sum churn risk
            total_churn_risk += comment.get("churn_risk", 0)

            # Count pain points
            for pain_point in comment.get("pain_points", []):
                pain_points_counter[pain_point] = pain_points_counter.get(pain_point, 0) + 1

    # Calculate NPS from original data
    for _, row in original_df.iterrows():
        nps_cat = calculate_nps_category(row['Nota'])
        nps_counts[nps_cat] += 1

    # Calculate averages and final metrics
    total_comments = len(all_comments)
    processing_time = time.time() - start_time

    # Average emotions
    avg_emotions = {
        emotion: total / total_comments
        for emotion, total in emotion_totals.items()
    } if total_comments > 0 else {}

    # NPS score
    total_responses = sum(nps_counts.values())
    nps_score = ((nps_counts["promoter"] - nps_counts["detractor"]) / total_responses * 100) if total_responses > 0 else 0

    # Top pain points
    top_pain_points = sorted(
        pain_points_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )[:20]

    # Churn distribution (simplified)
    avg_churn = total_churn_risk / total_comments if total_comments > 0 else 0
    high_churn_count = sum(1 for comment in all_comments if comment.get("churn_risk", 0) > 0.7)

    # Build final results structure
    results = {
        "task_id": task_id,
        "metadata": {
            "total_comments": total_comments,
            "processing_time_seconds": processing_time,
            "model_used": settings.AI_MODEL,
            "timestamp": datetime.utcnow().isoformat(),
            "language_distribution": language_counts,
            "batches_processed": len(batch_results)
        },
        "summary": {
            "nps": {
                "score": round(nps_score, 1),
                "promoters": nps_counts["promoter"],
                "promoters_percentage": round(nps_counts["promoter"] / total_responses * 100, 1) if total_responses > 0 else 0,
                "passives": nps_counts["passive"],
                "passives_percentage": round(nps_counts["passive"] / total_responses * 100, 1) if total_responses > 0 else 0,
                "detractors": nps_counts["detractor"],
                "detractors_percentage": round(nps_counts["detractor"] / total_responses * 100, 1) if total_responses > 0 else 0,
            },
            "emotions": {k: round(v, 3) for k, v in avg_emotions.items()},
            "churn_risk": {
                "average": round(avg_churn, 3),
                "high_risk_count": high_churn_count,
                "high_risk_percentage": round(high_churn_count / total_comments * 100, 1) if total_comments > 0 else 0,
                "distribution": {
                    "very_low": sum(1 for c in all_comments if c.get("churn_risk", 0) <= 0.2),
                    "low": sum(1 for c in all_comments if 0.2 < c.get("churn_risk", 0) <= 0.4),
                    "moderate": sum(1 for c in all_comments if 0.4 < c.get("churn_risk", 0) <= 0.6),
                    "high": sum(1 for c in all_comments if 0.6 < c.get("churn_risk", 0) <= 0.8),
                    "very_high": sum(1 for c in all_comments if c.get("churn_risk", 0) > 0.8),
                }
            },
            "pain_points": [
                {
                    "issue": issue,
                    "frequency": freq,
                    "percentage": round(freq / total_comments * 100, 1) if total_comments > 0 else 0,
                    "examples": []  # Could be populated with examples
                }
                for issue, freq in top_pain_points
            ],
            "sentiment_distribution": sentiment_counts
        },
        "rows": all_comments,
        "aggregated_insights": {
            "top_positive_themes": [],  # Could be extracted from positive comments
            "top_negative_themes": [],  # Could be extracted from negative comments
            "recommendations": [],  # Could be generated based on analysis
            "segment_analysis": {}  # Could be populated with segment-specific insights
        }
    }

    return results


def store_analysis_results(task_id: str, results: Dict[str, Any]):
    """Store analysis results in Redis."""
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


@celery_app.task
def cleanup_expired_tasks():
    """Cleanup expired tasks and results."""
    logger.info("Starting cleanup of expired tasks")

    try:
        # This would implement cleanup logic
        # For now, Redis TTL handles most cleanup automatically
        logger.info("Cleanup completed")
        return {"status": "completed", "cleaned_tasks": 0}

    except Exception as e:
        logger.error("Cleanup failed", error=str(e))
        raise