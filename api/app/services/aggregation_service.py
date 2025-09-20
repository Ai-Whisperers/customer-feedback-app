"""
Aggregation service for pain point analysis.
Aggregates and ranks pain points from individual comments.
"""

from typing import List, Dict, Any, Optional
from collections import Counter
import structlog

logger = structlog.get_logger()


def aggregate_pain_points(
    results: List[Dict[str, Any]], 
    top_n: int = 3
) -> Dict[str, Any]:
    """
    Aggregate pain points from analysis results to get top N.
    
    Args:
        results: List of analysis results with pain_point field
        top_n: Number of top pain points to return
        
    Returns:
        Dictionary with top pain points and statistics
    """
    # Extract all pain points
    pain_points = []

    for result in results:
        if isinstance(result, dict):
            # Handle dict format with pain_points array
            pains = result.get('pain_points', [])
            if pains and isinstance(pains, list):
                for pain in pains:
                    if pain and isinstance(pain, str) and len(pain) > 0:
                        normalized = pain.lower().strip()
                        if len(normalized) > 0:
                            pain_points.append(normalized)
        elif isinstance(result, list) and len(result) > 8:
            # Handle array format from optimized API
            pain = result[8] if isinstance(result[8], str) else None
            if pain:
                normalized = pain.lower().strip()
                if len(normalized) > 0:
                    pain_points.append(normalized)
    
    if not pain_points:
        logger.info("No pain points found in results")
        return {
            'top_pain_points': [],
            'total_with_pains': 0,
            'pain_percentage': 0.0
        }
    
    # Count frequencies
    counter = Counter(pain_points)
    total_comments = len(results)
    total_with_pains = len(pain_points)
    
    # Get top N
    top_pains = counter.most_common(top_n)
    
    # Format results
    formatted_pains = [
        {
            'issue': pain,
            'count': count,
            'percentage': round((count / total_comments) * 100, 1),
            'severity': calculate_pain_severity(pain, count, total_with_pains)
        }
        for pain, count in top_pains
    ]
    
    logger.info(
        "Pain points aggregated",
        total_comments=total_comments,
        total_with_pains=total_with_pains,
        unique_pains=len(counter),
        top_n=len(formatted_pains)
    )
    
    return {
        'top_pain_points': formatted_pains,
        'total_with_pains': total_with_pains,
        'pain_percentage': round((total_with_pains / total_comments) * 100, 1)
    }


def calculate_pain_severity(pain: str, count: int, total: int) -> float:
    """
    Calculate severity score for a pain point.
    
    Args:
        pain: Pain point keyword
        count: Frequency of this pain point
        total: Total number of pain points
        
    Returns:
        Severity score from 0 to 1
    """
    # Base severity from frequency
    frequency_score = count / total
    
    # Weight by keyword severity
    HIGH_SEVERITY_KEYWORDS = {
        'precio', 'caro', 'cobro', 'pago', 'fraude',
        'robo', 'estafa', 'engano', 'mentira',
        'pesimo', 'horrible', 'malo', 'error', 'falla'
    }
    
    MEDIUM_SEVERITY_KEYWORDS = {
        'espera', 'demora', 'lento', 'tiempo',
        'calidad', 'servicio', 'atencion',
        'problema', 'dificil', 'complicado'
    }
    
    keyword_weight = 1.0
    if pain.lower() in HIGH_SEVERITY_KEYWORDS:
        keyword_weight = 1.5
    elif pain.lower() in MEDIUM_SEVERITY_KEYWORDS:
        keyword_weight = 1.2
    
    # Calculate final severity (capped at 1.0)
    severity = min(frequency_score * keyword_weight, 1.0)
    
    return round(severity, 2)


def aggregate_emotions(results: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate average emotions across all results.
    
    Args:
        results: List of analysis results with emotions
        
    Returns:
        Dictionary with average emotion scores
    """
    emotion_totals = {
        'satisfaccion': 0.0,
        'frustracion': 0.0,
        'enojo': 0.0,
        'confianza': 0.0,
        'decepcion': 0.0,
        'confusion': 0.0,
        'anticipacion': 0.0
    }
    
    valid_count = 0
    
    for result in results:
        emotions = result.get('emotions', {})
        if emotions:
            valid_count += 1
            for emotion, score in emotions.items():
                if emotion in emotion_totals:
                    emotion_totals[emotion] += score
    
    if valid_count == 0:
        return emotion_totals
    
    # Calculate averages
    return {
        emotion: round(total / valid_count, 3)
        for emotion, total in emotion_totals.items()
    }


def calculate_nps_distribution(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate NPS distribution and score.
    
    Args:
        results: List of analysis results with NPS categories
        
    Returns:
        Dictionary with NPS metrics
    """
    categories = {
        'promoter': 0,
        'passive': 0,
        'detractor': 0
    }
    
    for result in results:
        nps_category = result.get('nps_category', 'passive')
        if nps_category in categories:
            categories[nps_category] += 1
    
    total = sum(categories.values())
    
    if total == 0:
        return {
            'distribution': categories,
            'score': 0,
            'percentages': {k: 0.0 for k in categories}
        }
    
    percentages = {
        k: round((v / total) * 100, 1) 
        for k, v in categories.items()
    }
    
    # Calculate NPS score
    nps_score = percentages['promoter'] - percentages['detractor']
    
    return {
        'distribution': categories,
        'score': round(nps_score, 1),
        'percentages': percentages
    }


def calculate_churn_risk_stats(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate churn risk statistics.
    
    Args:
        results: List of analysis results with churn_risk
        
    Returns:
        Dictionary with churn risk metrics
    """
    churn_risks = [
        r.get('churn_risk', 0.5) 
        for r in results 
        if 'churn_risk' in r
    ]
    
    if not churn_risks:
        return {
            'average': 0.5,
            'high_risk_count': 0,
            'high_risk_percentage': 0.0,
            'risk_distribution': {'low': 0, 'medium': 0, 'high': 0}
        }
    
    # Calculate statistics
    avg_risk = sum(churn_risks) / len(churn_risks)
    
    # Categorize risks
    risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
    high_risk_count = 0
    
    for risk in churn_risks:
        if risk < 0.3:
            risk_distribution['low'] += 1
        elif risk < 0.7:
            risk_distribution['medium'] += 1
        else:
            risk_distribution['high'] += 1
            high_risk_count += 1
    
    return {
        'average': round(avg_risk, 3),
        'high_risk_count': high_risk_count,
        'high_risk_percentage': round((high_risk_count / len(churn_risks)) * 100, 1),
        'risk_distribution': risk_distribution
    }
