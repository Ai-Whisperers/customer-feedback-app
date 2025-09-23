"""
Analysis orchestration service.
Coordinates the feedback analysis workflow.
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import pandas as pd
import structlog

from app.core.validation import (
    validate_required_columns,
    normalize_feedback_data,
    detect_dominant_language,
    calculate_nps_category
)
from app.core.file_parser import get_parser
from app.core.aggregation import (
    aggregate_emotions,
    aggregate_sentiments,
    aggregate_languages,
    aggregate_pain_points,
    calculate_churn_metrics,
    calculate_nps_metrics,
    build_metadata
)
from app.services.deduplication_service import (
    DeduplicationService,
    filter_trivial_comments
)
from app.services.aggregation_service import (
    aggregate_pain_points as aggregate_optimized_pain_points,
    aggregate_emotions as aggregate_optimized_emotions,
    calculate_nps_distribution,
    calculate_churn_risk_stats
)
from app.config import settings

logger = structlog.get_logger()


def load_and_validate_file(file_path: str) -> pd.DataFrame:
    """
    Load and validate uploaded file using modular parser.

    Args:
        file_path: Path to the uploaded file

    Returns:
        Validated dataframe

    Raises:
        ValueError: If file is invalid or missing required columns
    """
    try:
        # Use modular parser for loading and validation
        parser = get_parser()
        file_path_obj = Path(file_path)

        # Parse file with validation
        df, metadata = parser.parse_file(file_path_obj)

        # Log parsing results
        logger.info(
            "File parsed successfully",
            file_path=file_path,
            rows=metadata['total_rows'],
            has_nps=metadata.get('has_nps_column', False),
            parser_mode=metadata.get('parser_mode', 'base')
        )

        # Additional validation if needed
        missing_columns = validate_required_columns(df)
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        return df

    except Exception as e:
        logger.error("File loading failed", file_path=file_path, error=str(e))
        raise


def prepare_analysis_data(df: pd.DataFrame) -> tuple[List[str], List[int], Optional[str], Dict[str, Any]]:
    """
    Prepare data for analysis with deduplication.

    Args:
        df: Input dataframe

    Returns:
        Tuple of (comments, ratings, language_hint, dedup_info)
    """
    # Normalize data
    df = normalize_feedback_data(df)

    if df.empty:
        raise ValueError("No valid data found after normalization")

    all_comments = df['Comentario Final'].tolist()
    all_ratings = df['Nota'].tolist()

    # Apply deduplication
    dedup_service = DeduplicationService(threshold=0.85)
    unique_indices, duplicate_map = dedup_service.find_duplicates(all_comments)

    # Filter trivial comments from unique set
    filtered_indices = filter_trivial_comments(all_comments, unique_indices)

    # Get unique comments for API processing
    comments_for_api = [all_comments[i][:150] for i in filtered_indices]  # Truncate to 150 chars
    ratings = [all_ratings[i] for i in filtered_indices]

    # Detect dominant language
    sample_size = min(10, len(comments_for_api))
    language_hint = detect_dominant_language(comments_for_api[:sample_size]) if comments_for_api else None

    dedup_info = {
        'original_count': len(all_comments),
        'unique_count': len(unique_indices),
        'filtered_count': len(filtered_indices),
        'duplicate_map': duplicate_map,
        'filtered_indices': filtered_indices,
        'all_comments': all_comments,
        'all_ratings': all_ratings
    }

    logger.info(
        "Data prepared with deduplication",
        original=dedup_info['original_count'],
        unique=dedup_info['unique_count'],
        filtered=dedup_info['filtered_count'],
        reduction_pct=round((1 - dedup_info['filtered_count']/dedup_info['original_count']) * 100, 1),
        language_hint=language_hint
    )

    return comments_for_api, ratings, language_hint, dedup_info


def merge_batch_results(
    batch_results: List[Dict[str, Any]],
    original_df: pd.DataFrame,
    task_id: str,
    start_time: float,
    model_used: str = None,
    dedup_info: Dict[str, Any] = None
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
    api_results = []
    for batch_result in batch_results:
        comments = batch_result.get("comments", [])
        api_results.extend(comments)

    # If we have dedup info, expand results to include duplicates
    if dedup_info:
        all_comments = expand_results_with_duplicates(
            api_results,
            dedup_info['all_comments'],
            dedup_info['filtered_indices'],
            dedup_info['duplicate_map'],
            dedup_info.get('all_ratings', [])
        )
    else:
        all_comments = api_results

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


def expand_results_with_duplicates(
    api_results: List[Dict[str, Any]],
    all_comments: List[str],
    filtered_indices: List[int],
    duplicate_map: Dict[int, int],
    all_ratings: List[int] = None
) -> List[Dict[str, Any]]:
    """
    Expand API results to include duplicates.

    Args:
        api_results: Results from API for unique comments
        all_comments: All original comments
        filtered_indices: Indices that were sent to API
        duplicate_map: Map of duplicate indices to original

    Returns:
        Expanded list with results for all comments
    """
    # Create mapping from filtered index to api result
    index_to_result = {}
    for i, filtered_idx in enumerate(filtered_indices):
        if i < len(api_results):
            index_to_result[filtered_idx] = api_results[i]

    # Build complete results list
    complete_results = []

    for idx in range(len(all_comments)):
        if idx in duplicate_map:
            # This is a duplicate, get result from original
            original_idx = duplicate_map[idx]
            if original_idx in index_to_result:
                result = index_to_result[original_idx].copy()
                result['index'] = idx
                result['original_text'] = all_comments[idx]
                result['nota'] = all_ratings[idx] if all_ratings and idx < len(all_ratings) else 5
                result['is_duplicate'] = True
                complete_results.append(result)
            else:
                # Original not found, create default
                result = create_default_result(idx)
                result['original_text'] = all_comments[idx]
                result['nota'] = all_ratings[idx] if all_ratings and idx < len(all_ratings) else 5
                complete_results.append(result)
        elif idx in index_to_result:
            # This is a unique comment with API result
            result = index_to_result[idx].copy()
            result['index'] = idx
            result['original_text'] = all_comments[idx]
            result['nota'] = all_ratings[idx] if all_ratings and idx < len(all_ratings) else 5
            result['is_duplicate'] = False
            complete_results.append(result)
        else:
            # This was filtered out (trivial), create default
            result = create_default_result(idx)
            result['original_text'] = all_comments[idx]
            result['nota'] = all_ratings[idx] if all_ratings and idx < len(all_ratings) else 5
            complete_results.append(result)

    return complete_results


def create_default_result(index: int) -> Dict[str, Any]:
    """
    Create default result for trivial/filtered comments.

    Args:
        index: Comment index

    Returns:
        Default analysis result
    """
    return {
        'index': index,
        'emotions': {
            'satisfaccion': 0.5,
            'frustracion': 0.5,
            'enojo': 0.5,
            'confianza': 0.5,
            'decepcion': 0.5,
            'confusion': 0.5,
            'anticipacion': 0.5
        },
        'churn_risk': 0.5,
        'pain_points': [],
        'sentiment_score': 0.0,
        'language': 'es',
        'nps_category': 'passive',
        'is_trivial': True
    }