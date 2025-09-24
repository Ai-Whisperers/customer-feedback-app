"""
Event loop management for Celery workers.
Fixes async/sync conflicts enabling parallel processing.
"""

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Coroutine
import structlog

logger = structlog.get_logger()


class SafeEventLoopManager:
    """
    Manages event loops safely for Celery workers.
    Handles the conflict between Celery's sync nature and async OpenAI calls.
    """

    _thread_local = threading.local()

    @classmethod
    def get_or_create_loop(cls) -> asyncio.AbstractEventLoop:
        """Get existing loop or create new one for current thread."""

        if not hasattr(cls._thread_local, 'loop'):
            # Create new loop for this thread
            cls._thread_local.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._thread_local.loop)

        return cls._thread_local.loop

    @classmethod
    def run_async_in_worker(cls, coro: Coroutine) -> Any:
        """
        Run async code in Celery worker safely.
        Creates isolated event loop per thread.
        """

        try:
            # Try to get existing loop
            loop = asyncio.get_event_loop()

            if loop.is_running():
                # Loop already running, use thread pool
                logger.info("Event loop running, using thread pool")

                def run_in_new_loop():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        return new_loop.run_until_complete(coro)
                    finally:
                        new_loop.close()

                with ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(run_in_new_loop)
                    return future.result(timeout=60)
            else:
                # Loop not running, we can use it
                return loop.run_until_complete(coro)

        except RuntimeError as e:
            if "no running event loop" in str(e) or "There is no current event loop" in str(e):
                # No loop exists, create one
                logger.info("No event loop, creating new one")
                return asyncio.run(coro)
            raise