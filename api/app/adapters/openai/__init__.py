"""
OpenAI adapter package.
Provides structured AI analysis for customer feedback.
"""

from app.config import settings
from app.adapters.openai.analyzer import OpenAIAnalyzer


def create_analyzer():
    """
    Factory function to create appropriate analyzer based on configuration.
    """
    # Check if parallel processing is enabled
    if settings.ENABLE_PARALLEL_PROCESSING:
        try:
            # Try to import and use parallel processor
            from app.adapters.openai.parallel_processor import ParallelProcessor
            import redis

            # Try to create Redis connection for caching
            try:
                redis_client = redis.from_url(settings.REDIS_URL)
                redis_client.ping()  # Test connection
            except Exception as e:
                redis_client = None
                import structlog
                logger = structlog.get_logger()
                logger.warning("Redis not available for caching", error=str(e))

            # Create parallel processor wrapper
            processor = ParallelProcessor(redis_client)

            # Create a compatibility wrapper to match existing interface
            class AnalyzerWrapper:
                def __init__(self, processor):
                    self.processor = processor
                    self._analyzer = OpenAIAnalyzer()  # Keep original for compatibility

                async def analyze_batch(self, comments, batch_index=0, language_hint=None):
                    """Compatibility wrapper for analyze_batch."""
                    lang = language_hint.value if hasattr(language_hint, 'value') else 'es'
                    results = self.processor.process_comments(
                        comments,
                        language_hint=lang,
                        batch_size=None  # Use default from settings
                    )
                    # Convert to expected format
                    return {
                        "results": results,
                        "batch_index": batch_index
                    }

                def optimize_batch_size(self, comments):
                    """Compatibility wrapper for optimize_batch_size."""
                    batch_size = settings.BATCH_SIZE_OPTIMAL
                    return [
                        comments[i:i+batch_size]
                        for i in range(0, len(comments), batch_size)
                    ]

                # Delegate other methods to original analyzer
                def __getattr__(self, name):
                    return getattr(self._analyzer, name)

            return AnalyzerWrapper(processor)

        except ImportError:
            # Fallback to original analyzer if parallel processor not available
            pass

    # Default: use original analyzer
    return OpenAIAnalyzer()


# Create singleton instance
openai_analyzer = create_analyzer()

__all__ = ["openai_analyzer", "OpenAIAnalyzer", "create_analyzer"]