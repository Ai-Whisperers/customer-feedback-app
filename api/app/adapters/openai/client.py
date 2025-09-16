"""
OpenAI API client configuration and rate limiting.
"""

import asyncio
import time
from typing import Optional
import structlog
from openai import AsyncOpenAI

from app.config import settings

logger = structlog.get_logger()


class RateLimiter:
    """Rate limiter for OpenAI API calls."""

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


def create_rate_limiter(max_rps: Optional[int] = None) -> RateLimiter:
    """
    Create rate limiter for API calls.

    Args:
        max_rps: Maximum requests per second, defaults to settings

    Returns:
        Configured RateLimiter instance
    """
    if max_rps is None:
        max_rps = settings.MAX_RPS

    return RateLimiter(max_rps=max_rps)