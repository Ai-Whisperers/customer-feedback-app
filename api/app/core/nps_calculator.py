"""
NPS calculation module with configurable formulas.
Supports different NPS calculation methods via configuration.
"""

from typing import Dict, Any
from enum import Enum

from app.config import settings


class NPSMethod(Enum):
    """NPS calculation methods."""
    STANDARD = "standard"  # Standard formula: (promoters - detractors) / total * 100
    ABSOLUTE = "absolute"  # Absolute formula: abs((promoters - detractors) / total * 100)
    WEIGHTED = "weighted"  # Weighted formula with passive contribution
    SHIFTED = "shifted"    # Shifted formula: ((promoters - detractors) / total + 1) * 50


def calculate_nps_score(
    promoter_count: int,
    passive_count: int,
    detractor_count: int,
    method: str = None
) -> float:
    """
    Calculate NPS score using the configured method.

    Args:
        promoter_count: Number of promoters (9-10)
        passive_count: Number of passives (7-8)
        detractor_count: Number of detractors (0-6)
        method: Calculation method override (optional)

    Returns:
        NPS score value
    """
    if method is None:
        method = settings.NPS_CALCULATION_METHOD

    total_responses = promoter_count + passive_count + detractor_count

    if total_responses == 0:
        return 0.0

    if method == NPSMethod.ABSOLUTE.value:
        # Always returns positive value
        base_score = (promoter_count - detractor_count) / total_responses * 100
        return abs(base_score)

    elif method == NPSMethod.WEIGHTED.value:
        # Includes passive contribution with weight
        passive_weight = settings.NPS_PASSIVE_WEIGHT
        weighted_score = (
            promoter_count - detractor_count + (passive_count * passive_weight)
        ) / total_responses * 100
        return weighted_score

    elif method == NPSMethod.SHIFTED.value:
        # Shifts range to 0-100 instead of -100 to +100
        base_score = (promoter_count - detractor_count) / total_responses
        shifted_score = (base_score + 1) * 50
        return shifted_score

    else:  # NPSMethod.STANDARD.value or default
        # Standard NPS formula
        return (promoter_count - detractor_count) / total_responses * 100


def get_nps_interpretation(score: float, method: str = None) -> str:
    """
    Get interpretation of NPS score based on calculation method.

    Args:
        score: NPS score value
        method: Calculation method used

    Returns:
        Interpretation string
    """
    if method is None:
        method = settings.NPS_CALCULATION_METHOD

    if method == NPSMethod.SHIFTED.value:
        # Shifted scale interpretation (0-100)
        if score >= 75:
            return "excellent"
        elif score >= 50:
            return "good"
        elif score >= 25:
            return "needs_improvement"
        else:
            return "critical"
    else:
        # Standard scale interpretation (-100 to +100)
        if score >= 70:
            return "excellent"
        elif score >= 50:
            return "great"
        elif score >= 0:
            return "good"
        elif score >= -50:
            return "needs_improvement"
        else:
            return "critical"


def calculate_nps_metrics_modular(nps_counts: Dict[str, int]) -> Dict[str, Any]:
    """
    Calculate comprehensive NPS metrics using configured method.

    Args:
        nps_counts: Dictionary with promoter, passive, detractor counts

    Returns:
        Dictionary with NPS metrics
    """
    total_responses = sum(nps_counts.values())

    if total_responses == 0:
        return {
            "score": 50,  # Neutral score for shifted method when no data
            "method": settings.NPS_CALCULATION_METHOD,
            "promoters": 0,
            "promoters_percentage": 0,
            "passives": 0,
            "passives_percentage": 0,
            "detractors": 0,
            "detractors_percentage": 0,
            "interpretation": "no_data"
        }

    nps_score = calculate_nps_score(
        nps_counts.get("promoter", 0),
        nps_counts.get("passive", 0),
        nps_counts.get("detractor", 0)
    )

    method = settings.NPS_CALCULATION_METHOD

    return {
        "score": round(nps_score, 1),
        "method": method,
        "promoters": nps_counts.get("promoter", 0),
        "promoters_percentage": round(nps_counts.get("promoter", 0) / total_responses * 100, 1),
        "passives": nps_counts.get("passive", 0),
        "passives_percentage": round(nps_counts.get("passive", 0) / total_responses * 100, 1),
        "detractors": nps_counts.get("detractor", 0),
        "detractors_percentage": round(nps_counts.get("detractor", 0) / total_responses * 100, 1),
        "interpretation": get_nps_interpretation(nps_score, method)
    }