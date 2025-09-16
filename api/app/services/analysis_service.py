"""
Analysis orchestration service.
Coordinates the feedback analysis workflow.
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd
import structlog

from app.core.validation import (
    validate_required_columns,
    normalize_feedback_data,
    detect_dominant_language,
    calculate_nps_category
)
from app.core.aggregation import (
    aggregate_emotions,
    aggregate_sentiments,
    aggregate_languages,
    aggregate_pain_points,
    calculate_churn_metrics,
    calculate_nps_metrics,
    build_metadata
)
from app.config import settings

logger = structlog.get_logger()


def load_and_validate_file(file_path: str) -> pd.DataFrame:
    """
    Load and validate uploaded file.

    Args:
        file_path: Path to the uploaded file

    Returns:
        Validated dataframe

    Raises:
        ValueError: If file is invalid or missing required columns
    """
    try:
        # Determine file type and read
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path, encoding='utf-8')
        else:  # Excel files
            df = pd.read_excel(file_path)

        # Validate required columns
        missing_columns = validate_required_columns(df)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df

    except Exception as e:
        logger.error("File loading failed", file_path=file_path, error=str(e))
        raise


def prepare_analysis_data(df: pd.DataFrame) -> tuple[List[str], List[int], Optional[str]]:
    """
    Prepare data for analysis.

    Args:
        df: Input dataframe

    Returns:
        Tuple of (comments, ratings, language_hint)
    """
    # Normalize data
    df = normalize_feedback_data(df)

    if df.empty:
        raise ValueError("No valid data found after normalization")

    comments = df['Comentario Final'].tolist()
    ratings = df['Nota'].tolist()

    # Detect dominant language
    sample_size = min(10, len(comments))
    language_hint = detect_dominant_language(comments[:sample_size])

    logger.info(
        "Data prepared for analysis",
        total_comments=len(comments),
        language_hint=language_hint
    )

    return comments, ratings, language_hint


def merge_batch_results(
    batch_results: List[Dict[str, Any]],
    original_df: pd.DataFrame,
    task_id: str,
    start_time: float,
    model_used: str = None
) -> Dict[str, Any]:
    """
    Merge results from all batches into final results.

    Args:
        batch_results: List of batch analysis results
        original_df: Original dataframe with data
        task_id: Task identifier
        start_time: Processing start time
        model_used: AI model used for analysis

    Returns:
        Final merged results dictionary
    """
    logger.info("Merging batch results", task_id=task_id, batch_count=len(batch_results))

    # Extract all comments from batch results
    all_comments = []
    for batch_result in batch_results:
        comments = batch_result.get("comments", [])
        all_comments.extend(comments)

    # Aggregate metrics
    avg_emotions = aggregate_emotions(all_comments)
    sentiment_counts = aggregate_sentiments(all_comments)
    language_counts = aggregate_languages(all_comments)
    pain_points = aggregate_pain_points(all_comments)
    churn_metrics = calculate_churn_metrics(all_comments)

    # Calculate NPS from original data
    nps_counts = {"promoter": 0, "passive": 0, "detractor": 0}
    for _, row in original_df.iterrows():
        nps_cat = calculate_nps_category(row['Nota'])
        nps_counts[nps_cat] += 1

    nps_metrics = calculate_nps_metrics(nps_counts)

    # Calculate processing time
    processing_time = time.time() - start_time

    # Build metadata
    metadata = build_metadata(
        total_comments=len(all_comments),
        processing_time=processing_time,
        model_used=model_used or settings.AI_MODEL,
        language_counts=language_counts,
        batch_count=len(batch_results)
    )

    # Build final results structure
    results = {
        "task_id": task_id,
        "metadata": metadata,
        "summary": {
            "nps": nps_metrics,
            "emotions": avg_emotions,
            "churn_risk": churn_metrics,
            "pain_points": pain_points,
            "sentiment_distribution": sentiment_counts
        },
        "rows": all_comments,
        "aggregated_insights": {
            "top_positive_themes": [],
            "top_negative_themes": [],
            "recommendations": [],
            "segment_analysis": {}
        }
    }

    logger.info(
        "Results merged successfully",
        task_id=task_id,
        total_comments=len(all_comments),
        processing_time=processing_time
    )

    return results