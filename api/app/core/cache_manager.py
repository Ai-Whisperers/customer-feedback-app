"""
Cache manager for comment analysis results.
Reduces redundant API calls by caching similar comments.
"""

import hashlib
import json
from typing import Optional, Dict, Any, List, Tuple
import redis
import structlog
from datetime import timedelta

from app.config import settings

logger = structlog.get_logger()


class CommentCacheManager:
    """Manages caching of comment analysis results."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize cache manager.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client
        self.enabled = settings.ENABLE_COMMENT_CACHE
        self.ttl_seconds = settings.CACHE_TTL_DAYS * 24 * 3600
        self.namespace = "analysis:cache"

        # Statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "errors": 0
        }

    def get_cache_key(self, comment: str, language: str = "es") -> str:
        """
        Generate cache key for a comment.

        Args:
            comment: Comment text
            language: Language code

        Returns:
            Cache key string
        """
        # Normalize comment for consistent hashing
        normalized = comment.lower().strip()
        # Include language in hash to separate different language analyses
        content = f"{language}:{normalized}"
        hash_digest = hashlib.sha256(content.encode()).hexdigest()[:16]
        return f"{self.namespace}:{language}:{hash_digest}"

    def get(self, comment: str, language: str = "es") -> Optional[Dict[str, Any]]:
        """
        Get cached analysis for a comment.

        Args:
            comment: Comment text
            language: Language code

        Returns:
            Cached analysis or None
        """
        if not self.enabled or not self.redis:
            return None

        try:
            key = self.get_cache_key(comment, language)
            cached_data = self.redis.get(key)

            if cached_data:
                self.stats["hits"] += 1
                logger.debug(
                    "Cache hit",
                    key=key,
                    hit_rate=self._get_hit_rate()
                )
                return json.loads(cached_data)
            else:
                self.stats["misses"] += 1
                return None

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(
                "Cache get failed",
                error=str(e),
                comment_preview=comment[:50]
            )
            return None

    def set(
        self,
        comment: str,
        analysis: Dict[str, Any],
        language: str = "es"
    ) -> bool:
        """
        Cache analysis result for a comment.

        Args:
            comment: Comment text
            analysis: Analysis result
            language: Language code

        Returns:
            Success status
        """
        if not self.enabled or not self.redis:
            return False

        try:
            key = self.get_cache_key(comment, language)
            self.redis.setex(
                key,
                self.ttl_seconds,
                json.dumps(analysis)
            )
            logger.debug(
                "Cache set",
                key=key,
                ttl_days=settings.CACHE_TTL_DAYS
            )
            return True

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(
                "Cache set failed",
                error=str(e),
                comment_preview=comment[:50]
            )
            return False

    def get_many(
        self,
        comments: List[str],
        language: str = "es"
    ) -> Tuple[Dict[int, Dict[str, Any]], List[int]]:
        """
        Get cached analyses for multiple comments.

        Args:
            comments: List of comments
            language: Language code

        Returns:
            Tuple of (cached_results, uncached_indices)
        """
        if not self.enabled or not self.redis:
            return {}, list(range(len(comments)))

        try:
            # Generate all keys
            keys = [
                self.get_cache_key(comment, language)
                for comment in comments
            ]

            # Batch get from Redis
            cached_values = self.redis.mget(keys)

            # Process results
            cached_results = {}
            uncached_indices = []

            for i, (comment, cached_value) in enumerate(zip(comments, cached_values)):
                if cached_value:
                    try:
                        cached_results[i] = json.loads(cached_value)
                        self.stats["hits"] += 1
                    except json.JSONDecodeError:
                        uncached_indices.append(i)
                        self.stats["misses"] += 1
                else:
                    uncached_indices.append(i)
                    self.stats["misses"] += 1

            logger.info(
                "Batch cache check",
                total=len(comments),
                hits=len(cached_results),
                misses=len(uncached_indices),
                hit_rate=self._get_hit_rate()
            )

            return cached_results, uncached_indices

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(
                "Batch cache get failed",
                error=str(e),
                batch_size=len(comments)
            )
            return {}, list(range(len(comments)))

    def set_many(
        self,
        results: List[Tuple[str, Dict[str, Any]]],
        language: str = "es"
    ) -> int:
        """
        Cache multiple analysis results.

        Args:
            results: List of (comment, analysis) tuples
            language: Language code

        Returns:
            Number of successfully cached items
        """
        if not self.enabled or not self.redis:
            return 0

        try:
            pipe = self.redis.pipeline()
            count = 0

            for comment, analysis in results:
                key = self.get_cache_key(comment, language)
                pipe.setex(
                    key,
                    self.ttl_seconds,
                    json.dumps(analysis)
                )
                count += 1

            pipe.execute()

            logger.info(
                "Batch cache set",
                cached_count=count,
                ttl_days=settings.CACHE_TTL_DAYS
            )

            return count

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(
                "Batch cache set failed",
                error=str(e),
                batch_size=len(results)
            )
            return 0

    def clear_namespace(self) -> int:
        """
        Clear all cached analyses.

        Returns:
            Number of keys deleted
        """
        if not self.redis:
            return 0

        try:
            # Find all keys in namespace
            pattern = f"{self.namespace}:*"
            keys = list(self.redis.scan_iter(match=pattern))

            if keys:
                deleted = self.redis.delete(*keys)
                logger.info(
                    "Cache namespace cleared",
                    deleted_count=deleted
                )
                return deleted

            return 0

        except Exception as e:
            logger.error(
                "Cache clear failed",
                error=str(e)
            )
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        total_requests = self.stats["hits"] + self.stats["misses"]

        return {
            "enabled": self.enabled,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "errors": self.stats["errors"],
            "total_requests": total_requests,
            "hit_rate": self._get_hit_rate(),
            "ttl_days": settings.CACHE_TTL_DAYS
        }

    def _get_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total = self.stats["hits"] + self.stats["misses"]
        if total == 0:
            return 0.0
        return round(self.stats["hits"] / total, 3)


class BatchCacheProcessor:
    """Process batches with cache optimization."""

    def __init__(self, cache_manager: CommentCacheManager):
        """
        Initialize batch processor.

        Args:
            cache_manager: Cache manager instance
        """
        self.cache = cache_manager

    def split_cached_uncached(
        self,
        comments: List[str],
        language: str = "es"
    ) -> Tuple[Dict[int, Dict[str, Any]], List[Tuple[int, str]]]:
        """
        Split comments into cached and uncached.

        Args:
            comments: List of comments
            language: Language code

        Returns:
            Tuple of (cached_results, uncached_items)
        """
        cached_results, uncached_indices = self.cache.get_many(comments, language)

        # Build uncached items list with original indices
        uncached_items = [
            (idx, comments[idx])
            for idx in uncached_indices
        ]

        return cached_results, uncached_items

    def merge_results(
        self,
        cached_results: Dict[int, Dict[str, Any]],
        new_results: List[Dict[str, Any]],
        uncached_indices: List[int]
    ) -> List[Dict[str, Any]]:
        """
        Merge cached and new results in original order.

        Args:
            cached_results: Cached analysis results
            new_results: New analysis results
            uncached_indices: Indices of uncached items

        Returns:
            Complete results list in original order
        """
        # Create mapping of uncached index to new result
        new_results_map = {
            idx: result
            for idx, result in zip(uncached_indices, new_results)
        }

        # Combine all results
        all_results = {**cached_results, **new_results_map}

        # Sort by original index
        total_count = len(cached_results) + len(new_results)
        final_results = []

        for i in range(total_count):
            if i in all_results:
                final_results.append(all_results[i])
            else:
                logger.warning(
                    "Missing result for index",
                    index=i
                )
                # Add default result
                final_results.append({
                    "index": i,
                    "emotions": {},
                    "churn_risk": 0.5,
                    "pain_points": [],
                    "error": "Result not found"
                })

        return final_results

    def cache_new_results(
        self,
        comments: List[str],
        results: List[Dict[str, Any]],
        indices: List[int],
        language: str = "es"
    ) -> int:
        """
        Cache newly analyzed results.

        Args:
            comments: Original comments list
            results: Analysis results
            indices: Indices of analyzed comments
            language: Language code

        Returns:
            Number of cached items
        """
        # Build cache entries
        cache_entries = []
        for idx, result in zip(indices, results):
            if idx < len(comments):
                cache_entries.append((comments[idx], result))

        # Batch cache
        return self.cache.set_many(cache_entries, language)