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

from app.core.unified_file_processor import UnifiedFileProcessor
from app.core.unified_aggregation import UnifiedAggregator
from app.core.nps_calculator import categorize_rating
from app.services.efficient_deduplication import EfficientDeduplicationService
from app.config import settings

logger = structlog.get_logger()


def load_and_validate_file(file_path: str) -> pd.DataFrame:
    """
    Load and validate uploaded file using unified processor.

    Args:
        file_path: Path to the uploaded file

    Returns:
        Validated dataframe

    Raises:
        ValueError: If file is invalid or missing required columns
    """
    try:
        # Use unified processor for loading, validation, and normalization
        processor = UnifiedFileProcessor()
        file_path_obj = Path(file_path)

        # Process file with integrated validation
        df, metadata = processor.process_file(file_path_obj)

        # Log processing results
        logger.info(
            "File processed successfully",
            file_path=file_path,
            rows=metadata['total_rows'],
            valid_rows=metadata['valid_rows'],
            has_nps=metadata.get('has_nps_column', False),
            detected_language=metadata.get('detected_language', 'es')
        )

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
    # Data is already normalized by UnifiedFileProcessor
    if df.empty:
        raise ValueError("No valid data found")

    all_comments = df['Comentario Final'].tolist()
    all_ratings = df['Nota'].tolist()

    # Apply efficient O(n) deduplication
    dedup_service = EfficientDeduplicationService()
    (
        comments_for_api,
        ratings,
        filtered_indices,
        duplicate_map,
        dedup_info
    ) = dedup_service.deduplicate_comments(
        all_comments,
        all_ratings,
        similarity_threshold=0.85
    )

    # Truncate comments for API processing
    comments_for_api = [c[:150] for c in comments_for_api]

    # Get language hint from dataframe if available, otherwise detect
    if 'detected_language' in df.columns and not df['detected_language'].empty:
        language_hint = df['detected_language'].iloc[0]
    else:
        # Fallback detection if needed
        language_hint = 'es'  # Default to Spanish

    logger.info(
        "Data prepared with deduplication",
        original=dedup_info['original_count'],
        unique=dedup_info['filtered_count'],  # filtered_count is the unique count
        filtered=dedup_info['filtered_count'],
        reduction_pct=round((1 - dedup_info['filtered_count']/dedup_info['original_count']) * 100, 1) if dedup_info['original_count'] > 0 else 0,
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

    # Use unified aggregator
    aggregator = UnifiedAggregator()

    # Calculate NPS from original data (not from comments)
    nps_counts = {"promoter": 0, "passive": 0, "detractor": 0}
    for _, row in original_df.iterrows():
        nps_cat = categorize_rating(row['Nota'])
        nps_counts[nps_cat] += 1

    # Calculate all NPS metrics
    total = sum(nps_counts.values())
    if total > 0:
        promoters_pct = (nps_counts["promoter"] / total) * 100
        detractors_pct = (nps_counts["detractor"] / total) * 100
        passives_pct = (nps_counts["passive"] / total) * 100
        nps_score = promoters_pct - detractors_pct
    else:
        promoters_pct = detractors_pct = passives_pct = nps_score = 0

    nps_metrics = {
        "score": round(nps_score, 1),
        "promoters": nps_counts["promoter"],
        "promoters_percentage": round(promoters_pct, 1),
        "passives": nps_counts["passive"],
        "passives_percentage": round(passives_pct, 1),
        "detractors": nps_counts["detractor"],
        "detractors_percentage": round(detractors_pct, 1)
    }

    # Calculate processing time
    processing_time = time.time() - start_time

    # Use unified aggregator to format complete response
    results = aggregator.format_complete_response(
        task_id=task_id,
        comments=all_comments,
        processing_time=processing_time,
        model_used=model_used or settings.AI_MODEL,
        include_rows=True,
        nps_metrics=nps_metrics
    )

    # Update batch count in metadata
    results["metadata"]["batches_processed"] = len(batch_results)

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