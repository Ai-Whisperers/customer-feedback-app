"""
Core aggregation logic for analysis results.
Pure functions for aggregating and calculating metrics.
"""

from typing import Dict, List, Any, Tuple
from datetime import datetime
import structlog
from .nps_calculator import calculate_nps_metrics_modular

logger = structlog.get_logger()


def aggregate_emotions(comments: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Aggregate emotion scores from all comments.

    Args:
        comments: List of analyzed comments

    Returns:
        Dictionary of average emotion scores
    """
    if not comments:
        return {}

    emotion_totals = {}
    total_comments = len(comments)

    for comment in comments:
        emotions = comment.get("emotions", {})
        for emotion, value in emotions.items():
            emotion_totals[emotion] = emotion_totals.get(emotion, 0) + value

    # Calculate averages
    avg_emotions = {
        emotion: round(total / total_comments, 3)
        for emotion, total in emotion_totals.items()
    }

    return avg_emotions


def aggregate_sentiments(comments: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count sentiment distribution across comments.

    Args:
        comments: List of analyzed comments

    Returns:
        Dictionary of sentiment counts
    """
    sentiment_counts = {
        "muy_positivo": 0,
        "positivo": 0,
        "neutral": 0,
        "negativo": 0,
        "muy_negativo": 0
    }

    for comment in comments:
        sentiment = comment.get("sentiment", "neutral")
        if sentiment in sentiment_counts:
            sentiment_counts[sentiment] += 1

    return sentiment_counts


def aggregate_languages(comments: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Count language distribution across comments.

    Args:
        comments: List of analyzed comments

    Returns:
        Dictionary of language counts
    """
    language_counts = {"es": 0, "en": 0}

    for comment in comments:
        language = comment.get("language", "es")
        if language in language_counts:
            language_counts[language] += 1

    return language_counts


def aggregate_pain_points(comments: List[Dict[str, Any]], top_n: int = 20) -> List[Dict[str, Any]]:
    """
    Aggregate and rank pain points from comments.

    Args:
        comments: List of analyzed comments
        top_n: Number of top pain points to return

    Returns:
        List of top pain points with frequency and percentage
    """
    pain_points_counter = {}
    total_comments = len(comments)

    for comment in comments:
        for pain_point in comment.get("pain_points", []):
            pain_points_counter[pain_point] = pain_points_counter.get(pain_point, 0) + 1

    # Sort and get top N
    sorted_pain_points = sorted(
        pain_points_counter.items(),
        key=lambda x: x[1],
        reverse=True
    )[:top_n]

    # Format results
    formatted_pain_points = [
        {
            "issue": issue,
            "frequency": freq,
            "percentage": round(freq / total_comments * 100, 1) if total_comments > 0 else 0,
            "examples": []
        }
        for issue, freq in sorted_pain_points
    ]

    return formatted_pain_points


def calculate_churn_metrics(comments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate churn risk metrics from comments.

    Args:
        comments: List of analyzed comments

    Returns:
        Dictionary of churn risk metrics
    """
    if not comments:
        return {
            "average": 0,
            "high_risk_count": 0,
            "high_risk_percentage": 0,
            "distribution": {
                "very_low": 0,
                "low": 0,
                "moderate": 0,
                "high": 0,
                "very_high": 0
            }
        }

    total_churn_risk = sum(comment.get("churn_risk", 0) for comment in comments)
    total_comments = len(comments)
    avg_churn = total_churn_risk / total_comments

    # Count high risk
    high_risk_count = sum(1 for c in comments if c.get("churn_risk", 0) > 0.7)

    # Calculate distribution
    distribution = {
        "very_low": sum(1 for c in comments if c.get("churn_risk", 0) <= 0.2),
        "low": sum(1 for c in comments if 0.2 < c.get("churn_risk", 0) <= 0.4),
        "moderate": sum(1 for c in comments if 0.4 < c.get("churn_risk", 0) <= 0.6),
        "high": sum(1 for c in comments if 0.6 < c.get("churn_risk", 0) <= 0.8),
        "very_high": sum(1 for c in comments if c.get("churn_risk", 0) > 0.8),
    }

    return {
        "average": round(avg_churn, 3),
        "high_risk_count": high_risk_count,
        "high_risk_percentage": round(high_risk_count / total_comments * 100, 1),
        "distribution": distribution
    }


def calculate_nps_metrics(nps_counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate NPS score and percentages using the external modular calculator.

    Args:
        nps_counts: Dictionary with promoter, passive, detractor counts

    Returns:
        Dictionary of NPS metrics
    """
    # Delegate to the modular NPS calculator with configurable method
    return calculate_nps_metrics_modular(nps_counts)


def build_metadata(
    total_comments: int,
    processing_time: float,
    model_used: str,
    language_counts: Dict[str, int],
    batch_count: int
) -> Dict[str, Any]:
    """
    Build metadata section for results.

    Args:
        total_comments: Total number of comments analyzed
        processing_time: Time taken to process in seconds
        model_used: AI model used for analysis
        language_counts: Language distribution
        batch_count: Number of batches processed

    Returns:
        Dictionary of metadata
    """
    return {
        "total_comments": total_comments,
        "processing_time_seconds": round(processing_time, 2),
        "model_used": model_used,
        "timestamp": datetime.utcnow().isoformat(),
        "language_distribution": language_counts,
        "batches_processed": batch_count
    }