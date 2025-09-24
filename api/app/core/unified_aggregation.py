"""
Unified aggregation module consolidating all aggregation logic.
Preserves exact frontend contract for data format.
"""

from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter
import structlog
from datetime import datetime

logger = structlog.get_logger()


class UnifiedAggregator:
    """Single aggregator for all metrics to avoid duplication."""

    @staticmethod
    def aggregate_emotions(comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate emotion scores across all comments.
        Returns averages and top emotions.
        """
        if not comments:
            return {
                "averages": {},
                "top_5": [],
                "distribution": {}
            }

        # Single pass through data
        emotion_totals = defaultdict(lambda: {"sum": 0.0, "count": 0})

        for comment in comments:
            emotions = comment.get("emotions", {})
            for emotion, value in emotions.items():
                if isinstance(value, (int, float)):
                    emotion_totals[emotion]["sum"] += value
                    emotion_totals[emotion]["count"] += 1

        # Calculate averages
        averages = {}
        for emotion, data in emotion_totals.items():
            if data["count"] > 0:
                averages[emotion] = round(data["sum"] / data["count"], 3)

        # Get top emotions
        sorted_emotions = sorted(averages.items(), key=lambda x: x[1], reverse=True)
        top_5 = sorted_emotions[:5]

        # Calculate distribution
        distribution = {
            "high": len([e for e in averages.values() if e > 0.7]),
            "medium": len([e for e in averages.values() if 0.3 <= e <= 0.7]),
            "low": len([e for e in averages.values() if e < 0.3])
        }

        return {
            "averages": averages,
            "top_5": top_5,
            "distribution": distribution
        }

    @staticmethod
    def aggregate_sentiments(comments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Aggregate sentiment categories."""
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}

        for comment in comments:
            sentiment_score = comment.get("sentiment_score", 0)
            if sentiment_score > 0.1:
                sentiment_counts["positive"] += 1
            elif sentiment_score < -0.1:
                sentiment_counts["negative"] += 1
            else:
                sentiment_counts["neutral"] += 1

        return sentiment_counts

    @staticmethod
    def aggregate_pain_points(
        comments: List[Dict[str, Any]],
        top_n: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Aggregate pain points with examples.
        Returns format expected by frontend.
        """
        pain_counter = Counter()
        pain_examples = defaultdict(list)

        for comment in comments:
            pain_points = comment.get("pain_points", [])
            original_text = comment.get("original_text", "")

            for pain in pain_points:
                if pain:  # Skip empty strings
                    pain_counter[pain] += 1
                    # Collect up to 3 examples per pain point
                    if len(pain_examples[pain]) < 3 and original_text:
                        pain_examples[pain].append(original_text[:100])  # Truncate examples

        total = sum(pain_counter.values())

        # Format for frontend
        result = []
        for category, count in pain_counter.most_common(top_n):
            percentage = round((count / total * 100), 1) if total > 0 else 0
            result.append({
                "category": category,
                "count": count,
                "percentage": percentage,
                "examples": pain_examples.get(category, [])
            })

        return result

    @staticmethod
    def calculate_churn_metrics(comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate churn risk metrics.
        Returns format expected by frontend.
        """
        if not comments:
            return {
                "average": 0.0,
                "high_risk_count": 0,
                "high_risk_percentage": 0.0,
                "distribution": {}
            }

        churn_scores = []
        high_risk_count = 0

        # Distribution buckets
        distribution = {
            "0-0.2": 0,
            "0.2-0.4": 0,
            "0.4-0.6": 0,
            "0.6-0.8": 0,
            "0.8-1.0": 0
        }

        for comment in comments:
            risk = comment.get("churn_risk", 0.5)
            churn_scores.append(risk)

            if risk > 0.7:
                high_risk_count += 1

            # Add to distribution bucket
            if risk <= 0.2:
                distribution["0-0.2"] += 1
            elif risk <= 0.4:
                distribution["0.2-0.4"] += 1
            elif risk <= 0.6:
                distribution["0.4-0.6"] += 1
            elif risk <= 0.8:
                distribution["0.6-0.8"] += 1
            else:
                distribution["0.8-1.0"] += 1

        average = sum(churn_scores) / len(churn_scores) if churn_scores else 0
        high_risk_percentage = (high_risk_count / len(comments) * 100) if comments else 0

        return {
            "average": round(average, 3),
            "high_risk_count": high_risk_count,
            "high_risk_percentage": round(high_risk_percentage, 1),
            "distribution": distribution
        }

    @staticmethod
    def calculate_nps_metrics(comments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate NPS metrics from comments.
        Returns format expected by frontend.
        """
        nps_counts = {"promoter": 0, "passive": 0, "detractor": 0}

        for comment in comments:
            nps_category = comment.get("nps_category", "passive")
            if nps_category in nps_counts:
                nps_counts[nps_category] += 1

        total = sum(nps_counts.values())

        if total == 0:
            return {
                "score": 0,
                "promoters": 0,
                "promoters_percentage": 0,
                "passives": 0,
                "passives_percentage": 0,
                "detractors": 0,
                "detractors_percentage": 0
            }

        promoters_pct = (nps_counts["promoter"] / total) * 100
        detractors_pct = (nps_counts["detractor"] / total) * 100
        passives_pct = (nps_counts["passive"] / total) * 100

        nps_score = promoters_pct - detractors_pct

        return {
            "score": round(nps_score, 1),
            "promoters": nps_counts["promoter"],
            "promoters_percentage": round(promoters_pct, 1),
            "passives": nps_counts["passive"],
            "passives_percentage": round(passives_pct, 1),
            "detractors": nps_counts["detractor"],
            "detractors_percentage": round(detractors_pct, 1)
        }

    @staticmethod
    def calculate_language_distribution(comments: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate language distribution."""
        language_counts = Counter()

        for comment in comments:
            language = comment.get("language", "es")
            language_counts[language] += 1

        return dict(language_counts)

    @staticmethod
    def build_metadata(
        total_comments: int,
        processing_time: float,
        model_used: str,
        language_counts: Optional[Dict[str, int]] = None,
        batch_count: int = 1
    ) -> Dict[str, Any]:
        """
        Build metadata for response.
        Format must match frontend expectations exactly.
        """
        return {
            "total_comments": total_comments,
            "processing_time_seconds": round(processing_time, 2),
            "model_used": model_used,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "batches_processed": batch_count,
            "languages": language_counts or {"es": total_comments}
        }

    @staticmethod
    def format_summary_for_frontend(
        comments: List[Dict[str, Any]],
        nps_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format complete summary matching exact frontend contract.
        This is the main method that creates the 'summary' field.
        """
        aggregator = UnifiedAggregator()

        # Calculate all metrics
        emotion_data = aggregator.aggregate_emotions(comments)
        churn_data = aggregator.calculate_churn_metrics(comments)
        pain_points = aggregator.aggregate_pain_points(comments)

        # Use provided NPS or calculate from comments
        if nps_metrics is None:
            nps_metrics = aggregator.calculate_nps_metrics(comments)

        # Build summary in exact frontend format
        return {
            "nps": nps_metrics,
            "churn_risk": churn_data,
            "pain_points": pain_points,
            "emotions": emotion_data  # Additional data not required but useful
        }

    @staticmethod
    def format_complete_response(
        task_id: str,
        comments: List[Dict[str, Any]],
        processing_time: float,
        model_used: str,
        include_rows: bool = True,
        nps_metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Format complete response for frontend.
        Ensures all required fields are present and correctly typed.
        """
        aggregator = UnifiedAggregator()

        # Get language distribution
        language_counts = aggregator.calculate_language_distribution(comments)

        # Build metadata
        metadata = aggregator.build_metadata(
            total_comments=len(comments),
            processing_time=processing_time,
            model_used=model_used,
            language_counts=language_counts,
            batch_count=1  # Will be updated by caller if needed
        )

        # Build summary
        summary = aggregator.format_summary_for_frontend(comments, nps_metrics)

        # Format rows if needed
        rows = None
        if include_rows and comments:
            rows = []
            for comment in comments:
                row = {
                    "index": comment.get("index", 0),
                    "original_text": comment.get("original_text", ""),
                    "nota": int(comment.get("nota", 5)),
                    "nps_category": comment.get("nps_category", "passive"),
                    "sentiment": comment.get("sentiment", "neutral"),
                    "language": comment.get("language", "es"),
                    "churn_risk": float(comment.get("churn_risk", 0.5)),
                    "pain_points": comment.get("pain_points", []),
                    "emotions": comment.get("emotions", {})
                }
                rows.append(row)

        # Build complete response
        response = {
            "task_id": task_id,
            "metadata": metadata,
            "summary": summary,
            "rows": rows,
            "aggregated_insights": {
                "top_positive_themes": [],  # Legacy field
                "top_negative_themes": [],  # Legacy field
                "recommendations": [],       # Legacy field
                "segment_analysis": {}       # Legacy field
            }
        }

        return response