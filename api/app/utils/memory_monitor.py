"""
Memory monitoring for 512MB constraint on Render.
"""

import gc
import psutil
import structlog
from typing import Optional, Callable
from functools import wraps

logger = structlog.get_logger()


class MemoryMonitor:
    """
    Monitors and manages memory for 512MB constraint.
    """

    CRITICAL_THRESHOLD_MB = 450  # 90% of 512MB
    WARNING_THRESHOLD_MB = 400   # 78% of 512MB
    SAFE_THRESHOLD_MB = 300      # 58% of 512MB

    @classmethod
    def get_available_memory_mb(cls) -> float:
        """Get available memory in MB."""
        return psutil.virtual_memory().available / (1024 * 1024)

    @classmethod
    def get_used_memory_mb(cls) -> float:
        """Get used memory by current process in MB."""
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)

    @classmethod
    def check_memory_status(cls) -> str:
        """
        Check memory status.
        Returns: 'critical', 'warning', 'safe'
        """
        used = cls.get_used_memory_mb()

        if used > cls.CRITICAL_THRESHOLD_MB:
            return 'critical'
        elif used > cls.WARNING_THRESHOLD_MB:
            return 'warning'
        else:
            return 'safe'

    @classmethod
    def force_cleanup(cls):
        """Force garbage collection and log memory."""
        before = cls.get_used_memory_mb()

        # Force garbage collection
        gc.collect()

        after = cls.get_used_memory_mb()
        freed = before - after

        logger.info(
            "Memory cleanup performed",
            before_mb=round(before, 1),
            after_mb=round(after, 1),
            freed_mb=round(freed, 1)
        )

        return freed

    @classmethod
    def calculate_safe_batch_size(cls, total_items: int, base_batch_size: int = 100) -> int:
        """
        Calculate safe batch size based on available memory.
        """
        status = cls.check_memory_status()

        if status == 'critical':
            # Minimal batches
            return min(10, total_items)
        elif status == 'warning':
            # Reduced batches
            return min(30, base_batch_size // 2)
        else:
            # Normal batches
            return min(base_batch_size, total_items)

    @classmethod
    def memory_aware_decorator(cls, cleanup_after: bool = True):
        """
        Decorator to monitor memory usage of functions.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check before
                before = cls.get_used_memory_mb()
                status = cls.check_memory_status()

                if status == 'critical':
                    logger.warning(f"Critical memory before {func.__name__}: {before:.1f}MB")
                    cls.force_cleanup()

                try:
                    # Execute function
                    result = func(*args, **kwargs)

                    # Check after
                    after = cls.get_used_memory_mb()
                    used = after - before

                    logger.info(
                        f"Memory usage for {func.__name__}",
                        used_mb=round(used, 1),
                        total_mb=round(after, 1)
                    )

                    return result

                finally:
                    if cleanup_after:
                        cls.force_cleanup()

            return wrapper
        return decorator