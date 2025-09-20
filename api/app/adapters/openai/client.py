"""
OpenAI API client configuration and rate limiting.
"""

import asyncio
import time
from typing import Optional
import structlog
import redis
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger()


class GlobalRateLimiter:
    """Global rate limiter using Redis for coordination across workers."""

    def __init__(self, max_rps: int = 8):
        """
        Initialize global rate limiter.

        Args:
            max_rps: Maximum requests per second across all workers
        """
        self.max_rps = max_rps
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.key = "openai_rate_limit"

    async def acquire(self):
        """Acquire permission to make a request using Redis coordination."""
        while True:
            try:
                # Use Redis pipeline for atomic operations
                pipe = self.redis_client.pipeline()
                now = time.time()

                # Clean old entries and count current requests
                pipe.zremrangebyscore(self.key, 0, now - 1.0)
                pipe.zcard(self.key)
                pipe.zadd(self.key, {str(now): now})
                pipe.expire(self.key, 2)  # TTL for cleanup

                results = pipe.execute()
                current_count = results[1]  # Count after cleanup

                if current_count < self.max_rps:
                    # Permission granted
                    break
                else:
                    # Wait before retrying
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.warning("Rate limiter Redis error, using fallback", error=str(e))
                # Fallback: simple delay
                await asyncio.sleep(1.0 / self.max_rps)
                break


class RateLimiter:
    """Local rate limiter for OpenAI API calls (fallback)."""

    def __init__(self, max_rps: int = 8):
        """
        Initialize rate limiter.

        Args:
            max_rps: Maximum requests per second
        """
        self.max_rps = max_rps
        self.request_times = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 second
            self.request_times = [t for t in self.request_times if now - t < 1.0]

            # If we're at the limit, wait
            if len(self.request_times) >= self.max_rps:
                sleep_time = 1.0 - (now - self.request_times[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            # Record this request
            self.request_times.append(time.time())


def create_openai_client() -> AsyncOpenAI:
    """
    Create and configure OpenAI client.

    Returns:
        Configured AsyncOpenAI client
    """
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


def create_rate_limiter(max_rps: Optional[int] = None) -> GlobalRateLimiter:
    """
    Create global rate limiter for API calls.

    Args:
        max_rps: Maximum requests per second across all workers, defaults to settings

    Returns:
        Configured GlobalRateLimiter instance
    """
    if max_rps is None:
        max_rps = settings.MAX_RPS

    return GlobalRateLimiter(max_rps=max_rps)