"""
Token and performance metrics service with Redis persistence.
Provides real-time visibility into OpenAI API usage and costs.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import structlog

from app.infrastructure.cache import CacheClient
from app.config import settings

logger = structlog.get_logger()


class MetricsService:
    """
    Centralized metrics service for tracking OpenAI usage and performance.

    Persists metrics to Redis for historical tracking and real-time dashboard.
    """

    # Redis keys
    GLOBAL_METRICS_KEY = "metrics:global"
    TASK_METRICS_PREFIX = "metrics:task:"
    HOURLY_METRICS_PREFIX = "metrics:hourly:"
    DAILY_METRICS_PREFIX = "metrics:daily:"

    # GPT-4o-mini pricing (as of 2025-01)
    PRICE_PER_1M_INPUT_TOKENS = 0.15  # $0.15 per 1M input tokens
    PRICE_PER_1M_OUTPUT_TOKENS = 0.60  # $0.60 per 1M output tokens

    @classmethod
    def update_global_metrics(
        cls,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        total_tokens: int = 0,
        comments_processed: int = 0,
        batches_processed: int = 0,
        duration_seconds: float = 0,
        task_id: str = None
    ) -> None:
        """
        Update global metrics with new data.

        Args:
            prompt_tokens: Input tokens used
            completion_tokens: Output tokens used
            total_tokens: Total tokens used
            comments_processed: Number of comments analyzed
            batches_processed: Number of batches processed
            duration_seconds: Processing duration
            task_id: Optional task ID for task-specific tracking
        """
        try:
            redis_client = CacheClient.get_client()

            # Get current metrics
            current = redis_client.get(cls.GLOBAL_METRICS_KEY)
            if current:
                metrics = json.loads(current)
            else:
                metrics = cls._get_empty_metrics()

            # Update metrics
            metrics['total_requests'] += 1 if batches_processed > 0 else 0
            metrics['total_prompt_tokens'] += prompt_tokens
            metrics['total_completion_tokens'] += completion_tokens
            metrics['total_tokens'] += total_tokens
            metrics['total_comments'] += comments_processed
            metrics['total_batches'] += batches_processed
            metrics['total_duration_seconds'] += duration_seconds
            metrics['last_updated'] = datetime.utcnow().isoformat()

            # Calculate averages
            if metrics['total_requests'] > 0:
                metrics['avg_tokens_per_request'] = round(
                    metrics['total_tokens'] / metrics['total_requests'], 2
                )
            if metrics['total_comments'] > 0:
                metrics['avg_tokens_per_comment'] = round(
                    metrics['total_tokens'] / metrics['total_comments'], 2
                )

            # Calculate costs
            input_cost = (metrics['total_prompt_tokens'] / 1_000_000) * cls.PRICE_PER_1M_INPUT_TOKENS
            output_cost = (metrics['total_completion_tokens'] / 1_000_000) * cls.PRICE_PER_1M_OUTPUT_TOKENS
            metrics['total_cost_usd'] = round(input_cost + output_cost, 4)

            # Save to Redis with 7-day TTL
            redis_client.setex(
                cls.GLOBAL_METRICS_KEY,
                604800,  # 7 days
                json.dumps(metrics)
            )

            # Also save task-specific metrics
            if task_id:
                cls._update_task_metrics(
                    task_id, prompt_tokens, completion_tokens,
                    total_tokens, comments_processed, batches_processed, duration_seconds
                )

            # Update hourly/daily aggregates
            cls._update_time_based_metrics(
                prompt_tokens, completion_tokens, total_tokens,
                comments_processed, batches_processed
            )

            logger.info(
                "Metrics updated",
                total_tokens=metrics['total_tokens'],
                total_cost=metrics['total_cost_usd'],
                requests=metrics['total_requests']
            )

        except Exception as e:
            logger.error("Failed to update metrics", error=str(e))

    @classmethod
    def get_global_metrics(cls) -> Dict[str, Any]:
        """Get current global metrics."""
        try:
            redis_client = CacheClient.get_client()
            current = redis_client.get(cls.GLOBAL_METRICS_KEY)

            if current:
                return json.loads(current)
            else:
                return cls._get_empty_metrics()

        except Exception as e:
            logger.error("Failed to get metrics", error=str(e))
            return cls._get_empty_metrics()

    @classmethod
    def get_task_metrics(cls, task_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific task."""
        try:
            redis_client = CacheClient.get_client()
            key = f"{cls.TASK_METRICS_PREFIX}{task_id}"
            metrics = redis_client.get(key)

            if metrics:
                return json.loads(metrics)
            return None

        except Exception as e:
            logger.error("Failed to get task metrics", task_id=task_id, error=str(e))
            return None

    @classmethod
    def get_recent_metrics(cls, hours: int = 1) -> Dict[str, Any]:
        """
        Get metrics for the last N hours.

        Args:
            hours: Number of hours to look back

        Returns:
            Aggregated metrics for the time period
        """
        try:
            redis_client = CacheClient.get_client()

            # Get hourly metrics for the period
            now = datetime.utcnow()
            hourly_data = []

            for i in range(hours):
                timestamp = now - timedelta(hours=i)
                hour_key = timestamp.strftime("%Y%m%d%H")
                key = f"{cls.HOURLY_METRICS_PREFIX}{hour_key}"

                data = redis_client.get(key)
                if data:
                    hourly_data.append(json.loads(data))

            # Aggregate
            if hourly_data:
                aggregated = {
                    'period_hours': hours,
                    'total_tokens': sum(h.get('total_tokens', 0) for h in hourly_data),
                    'total_comments': sum(h.get('total_comments', 0) for h in hourly_data),
                    'total_requests': sum(h.get('total_requests', 0) for h in hourly_data),
                    'hourly_breakdown': hourly_data
                }

                # Calculate cost
                total_prompt = sum(h.get('prompt_tokens', 0) for h in hourly_data)
                total_completion = sum(h.get('completion_tokens', 0) for h in hourly_data)
                input_cost = (total_prompt / 1_000_000) * cls.PRICE_PER_1M_INPUT_TOKENS
                output_cost = (total_completion / 1_000_000) * cls.PRICE_PER_1M_OUTPUT_TOKENS
                aggregated['total_cost_usd'] = round(input_cost + output_cost, 4)

                return aggregated
            else:
                return {
                    'period_hours': hours,
                    'total_tokens': 0,
                    'total_comments': 0,
                    'total_requests': 0,
                    'total_cost_usd': 0,
                    'hourly_breakdown': []
                }

        except Exception as e:
            logger.error("Failed to get recent metrics", error=str(e))
            return {'error': str(e)}

    @classmethod
    def get_dashboard_data(cls) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data.

        Returns:
            Complete metrics for dashboard display
        """
        global_metrics = cls.get_global_metrics()
        recent_1h = cls.get_recent_metrics(hours=1)
        recent_24h = cls.get_recent_metrics(hours=24)

        return {
            'timestamp': datetime.utcnow().isoformat(),
            'global': global_metrics,
            'last_hour': recent_1h,
            'last_24_hours': recent_24h,
            'pricing': {
                'model': settings.AI_MODEL,
                'input_per_1m_tokens': cls.PRICE_PER_1M_INPUT_TOKENS,
                'output_per_1m_tokens': cls.PRICE_PER_1M_OUTPUT_TOKENS,
                'currency': 'USD'
            }
        }

    @classmethod
    def reset_metrics(cls) -> None:
        """Reset all metrics (use with caution)."""
        try:
            redis_client = CacheClient.get_client()
            redis_client.delete(cls.GLOBAL_METRICS_KEY)
            logger.warning("Global metrics reset")
        except Exception as e:
            logger.error("Failed to reset metrics", error=str(e))

    @classmethod
    def _get_empty_metrics(cls) -> Dict[str, Any]:
        """Get empty metrics structure."""
        return {
            'total_requests': 0,
            'total_prompt_tokens': 0,
            'total_completion_tokens': 0,
            'total_tokens': 0,
            'total_comments': 0,
            'total_batches': 0,
            'total_duration_seconds': 0,
            'avg_tokens_per_request': 0,
            'avg_tokens_per_comment': 0,
            'total_cost_usd': 0,
            'last_updated': datetime.utcnow().isoformat()
        }

    @classmethod
    def _update_task_metrics(
        cls,
        task_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        comments: int,
        batches: int,
        duration: float
    ) -> None:
        """Update metrics for a specific task."""
        try:
            redis_client = CacheClient.get_client()
            key = f"{cls.TASK_METRICS_PREFIX}{task_id}"

            metrics = {
                'task_id': task_id,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_tokens': total_tokens,
                'comments_processed': comments,
                'batches_processed': batches,
                'duration_seconds': duration,
                'timestamp': datetime.utcnow().isoformat()
            }

            # Calculate cost
            input_cost = (prompt_tokens / 1_000_000) * cls.PRICE_PER_1M_INPUT_TOKENS
            output_cost = (completion_tokens / 1_000_000) * cls.PRICE_PER_1M_OUTPUT_TOKENS
            metrics['cost_usd'] = round(input_cost + output_cost, 4)

            # Save with 24h TTL
            redis_client.setex(key, 86400, json.dumps(metrics))

        except Exception as e:
            logger.error("Failed to update task metrics", task_id=task_id, error=str(e))

    @classmethod
    def _update_time_based_metrics(
        cls,
        prompt_tokens: int,
        completion_tokens: int,
        total_tokens: int,
        comments: int,
        batches: int
    ) -> None:
        """Update hourly and daily metric aggregates."""
        try:
            redis_client = CacheClient.get_client()
            now = datetime.utcnow()

            # Hourly metrics
            hour_key = f"{cls.HOURLY_METRICS_PREFIX}{now.strftime('%Y%m%d%H')}"
            hourly = redis_client.get(hour_key)

            if hourly:
                hourly_data = json.loads(hourly)
            else:
                hourly_data = {
                    'hour': now.strftime('%Y-%m-%d %H:00'),
                    'total_requests': 0,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'total_comments': 0,
                    'total_batches': 0
                }

            hourly_data['total_requests'] += 1 if batches > 0 else 0
            hourly_data['prompt_tokens'] += prompt_tokens
            hourly_data['completion_tokens'] += completion_tokens
            hourly_data['total_tokens'] += total_tokens
            hourly_data['total_comments'] += comments
            hourly_data['total_batches'] += batches

            # Save with 48h TTL
            redis_client.setex(hour_key, 172800, json.dumps(hourly_data))

            # Daily metrics (similar pattern)
            day_key = f"{cls.DAILY_METRICS_PREFIX}{now.strftime('%Y%m%d')}"
            daily = redis_client.get(day_key)

            if daily:
                daily_data = json.loads(daily)
            else:
                daily_data = {
                    'date': now.strftime('%Y-%m-%d'),
                    'total_requests': 0,
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_tokens': 0,
                    'total_comments': 0,
                    'total_batches': 0
                }

            daily_data['total_requests'] += 1 if batches > 0 else 0
            daily_data['prompt_tokens'] += prompt_tokens
            daily_data['completion_tokens'] += completion_tokens
            daily_data['total_tokens'] += total_tokens
            daily_data['total_comments'] += comments
            daily_data['total_batches'] += batches

            # Save with 30-day TTL
            redis_client.setex(day_key, 2592000, json.dumps(daily_data))

        except Exception as e:
            logger.error("Failed to update time-based metrics", error=str(e))
