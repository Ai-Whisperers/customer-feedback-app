"""
Parallel processing orchestrator for OpenAI analysis.
Integrates async analyzer with cache management.
"""

import asyncio
from typing import List, Dict, Any, Optional, Tuple
import structlog
import redis
from datetime import datetime

from app.config import settings
from app.core.cache_manager import CommentCacheManager, BatchCacheProcessor
from .async_analyzer import AsyncOpenAIAnalyzer
from .analyzer import OpenAIAnalyzer  # Fallback to sync analyzer

logger = structlog.get_logger()


class ParallelProcessor:
    """Orchestrates parallel processing with caching."""

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """
        Initialize parallel processor.

        Args:
            redis_client: Redis client for caching
        """
        self.redis_client = redis_client
        self.use_parallel = settings.ENABLE_PARALLEL_PROCESSING
        self.use_cache = settings.ENABLE_COMMENT_CACHE and redis_client is not None

        # Initialize components
        if self.use_cache:
            self.cache_manager = CommentCacheManager(redis_client)
            self.batch_processor = BatchCacheProcessor(self.cache_manager)
        else:
            self.cache_manager = None
            self.batch_processor = None

        # Fallback sync analyzer
        self.sync_analyzer = OpenAIAnalyzer()

    def process_comments(
        self,
        comments: List[str],
        language_hint: str = "es",
        batch_size: Optional[int] = None,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Process comments with optimal strategy.

        Args:
            comments: List of comments to analyze
            language_hint: Language hint
            batch_size: Batch size for processing
            progress_callback: Progress callback function

        Returns:
            List of analysis results
        """
        start_time = datetime.now()

        # Determine batch size
        batch_size = batch_size or settings.BATCH_SIZE_OPTIMAL

        # Log processing start
        logger.info(
            "Starting comment processing",
            total_comments=len(comments),
            batch_size=batch_size,
            use_parallel=self.use_parallel,
            use_cache=self.use_cache
        )

        # Process based on configuration
        if self.use_parallel:
            results = self._process_parallel(
                comments,
                language_hint,
                batch_size,
                progress_callback
            )
        else:
            results = self._process_sequential(
                comments,
                language_hint,
                batch_size,
                progress_callback
            )

        # Log completion
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(
            "Processing completed",
            total_comments=len(comments),
            elapsed_seconds=elapsed,
            avg_per_comment=elapsed / len(comments) if comments else 0
        )

        # Alert if over threshold
        if elapsed > settings.ALERT_THRESHOLD_SECONDS:
            logger.warning(
                "Processing exceeded threshold",
                elapsed_seconds=elapsed,
                threshold_seconds=settings.ALERT_THRESHOLD_SECONDS
            )

        return results

    def _process_parallel(
        self,
        comments: List[str],
        language_hint: str,
        batch_size: int,
        progress_callback: Optional[callable]
    ) -> List[Dict[str, Any]]:
        """
        Process comments using parallel async processing.

        Args:
            comments: Comments to process
            language_hint: Language hint
            batch_size: Batch size
            progress_callback: Progress callback

        Returns:
            Analysis results
        """
        # Create event loop if not exists
        try:
            loop = asyncio.get_event_loop()
            if loop.is_closed():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        # Run async processing
        return loop.run_until_complete(
            self._async_process(
                comments,
                language_hint,
                batch_size,
                progress_callback
            )
        )

    async def _async_process(
        self,
        comments: List[str],
        language_hint: str,
        batch_size: int,
        progress_callback: Optional[callable]
    ) -> List[Dict[str, Any]]:
        """
        Async processing implementation.

        Args:
            comments: Comments to process
            language_hint: Language hint
            batch_size: Batch size
            progress_callback: Progress callback

        Returns:
            Analysis results
        """
        # Step 1: Check cache if enabled
        cached_results = {}
        uncached_indices = list(range(len(comments)))

        if self.use_cache and self.batch_processor:
            cached_results, uncached_items = self.batch_processor.split_cached_uncached(
                comments,
                language_hint
            )
            uncached_indices = [idx for idx, _ in uncached_items]

            logger.info(
                "Cache check completed",
                cached_count=len(cached_results),
                uncached_count=len(uncached_indices),
                cache_hit_rate=len(cached_results) / len(comments) if comments else 0
            )

        # Step 2: Process uncached comments
        new_results = []
        if uncached_indices:
            # Get uncached comments
            uncached_comments = [comments[idx] for idx in uncached_indices]

            # Create batches
            batches = [
                uncached_comments[i:i+batch_size]
                for i in range(0, len(uncached_comments), batch_size)
            ]

            # Process with async analyzer
            async with AsyncOpenAIAnalyzer() as analyzer:
                new_results = await analyzer.analyze_all_batches(
                    batches,
                    language_hint,
                    progress_callback
                )

            # Cache new results
            if self.use_cache and self.batch_processor:
                cached_count = self.batch_processor.cache_new_results(
                    comments,
                    new_results,
                    uncached_indices,
                    language_hint
                )
                logger.info(
                    "New results cached",
                    cached_count=cached_count
                )

        # Step 3: Merge results
        if self.batch_processor:
            final_results = self.batch_processor.merge_results(
                cached_results,
                new_results,
                uncached_indices
            )
        else:
            final_results = new_results

        return final_results

    def _process_sequential(
        self,
        comments: List[str],
        language_hint: str,
        batch_size: int,
        progress_callback: Optional[callable]
    ) -> List[Dict[str, Any]]:
        """
        Process comments sequentially (fallback).

        Args:
            comments: Comments to process
            language_hint: Language hint
            batch_size: Batch size
            progress_callback: Progress callback

        Returns:
            Analysis results
        """
        logger.info("Using sequential processing (fallback)")

        # Check cache first if enabled
        cached_results = {}
        uncached_indices = list(range(len(comments)))

        if self.use_cache and self.batch_processor:
            cached_results, uncached_items = self.batch_processor.split_cached_uncached(
                comments,
                language_hint
            )
            uncached_indices = [idx for idx, _ in uncached_items]

        # Process uncached
        new_results = []
        if uncached_indices:
            uncached_comments = [comments[idx] for idx in uncached_indices]

            # Create batches
            batches = [
                uncached_comments[i:i+batch_size]
                for i in range(0, len(uncached_comments), batch_size)
            ]

            # Process with sync analyzer
            for i, batch in enumerate(batches):
                batch_results = self.sync_analyzer.analyze_batch(
                    batch,
                    language_hint
                )
                new_results.extend(batch_results)

                # Update progress
                if progress_callback:
                    progress = int(((i + 1) / len(batches)) * 100)
                    progress_callback(progress)

            # Cache results
            if self.use_cache and self.batch_processor:
                self.batch_processor.cache_new_results(
                    comments,
                    new_results,
                    uncached_indices,
                    language_hint
                )

        # Merge results
        if self.batch_processor:
            final_results = self.batch_processor.merge_results(
                cached_results,
                new_results,
                uncached_indices
            )
        else:
            final_results = new_results

        return final_results

    def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics.

        Returns:
            Statistics dictionary
        """
        stats = {
            "parallel_enabled": self.use_parallel,
            "cache_enabled": self.use_cache,
            "concurrent_workers": settings.OPENAI_CONCURRENT_WORKERS,
            "batch_size": settings.BATCH_SIZE_OPTIMAL,
            "rate_limit_rps": settings.MAX_RPS
        }

        # Add cache stats if available
        if self.cache_manager:
            stats["cache"] = self.cache_manager.get_stats()

        return stats


def create_processor(redis_client: Optional[redis.Redis] = None) -> ParallelProcessor:
    """
    Factory function to create processor.

    Args:
        redis_client: Redis client

    Returns:
        ParallelProcessor instance
    """
    return ParallelProcessor(redis_client)