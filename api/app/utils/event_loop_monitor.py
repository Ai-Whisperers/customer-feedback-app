"""
Event loop monitoring module for debugging async/sync conflicts.
Provides non-intrusive monitoring of asyncio event loops across the pipeline.
"""

import asyncio
import threading
import traceback
import inspect
from functools import wraps
from typing import Any, Callable, Optional, Dict
import structlog
from datetime import datetime

logger = structlog.get_logger()


class EventLoopMonitor:
    """Monitor and track event loop states across the application."""

    def __init__(self):
        """Initialize the monitor."""
        self.loop_history = []
        self.max_history = 100
        self.enabled = True  # Can be disabled via environment

    def get_loop_info(self) -> Dict[str, Any]:
        """
        Get current event loop information.

        Returns:
            Dictionary with loop state information
        """
        info = {
            'timestamp': datetime.now().isoformat(),
            'thread_id': threading.current_thread().ident,
            'thread_name': threading.current_thread().name,
            'process_id': None,
            'loop_exists': False,
            'loop_running': False,
            'loop_closed': False,
            'loop_id': None,
            'stack_trace': None,
            'caller_info': None
        }

        try:
            import os
            info['process_id'] = os.getpid()
        except:
            pass

        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            info['loop_exists'] = True
            info['loop_id'] = id(loop)
            info['loop_running'] = loop.is_running()
            info['loop_closed'] = loop.is_closed()

            # Get policy info
            policy = asyncio.get_event_loop_policy()
            info['policy_class'] = policy.__class__.__name__

        except RuntimeError as e:
            info['loop_error'] = str(e)
        except Exception as e:
            info['unexpected_error'] = str(e)

        # Get caller information
        try:
            frame = inspect.currentframe()
            if frame and frame.f_back and frame.f_back.f_back:
                caller_frame = frame.f_back.f_back
                info['caller_info'] = {
                    'filename': caller_frame.f_code.co_filename,
                    'function': caller_frame.f_code.co_name,
                    'line': caller_frame.f_lineno
                }
        except:
            pass

        # Get limited stack trace for context
        try:
            stack_summary = traceback.extract_stack(limit=5)
            info['stack_trace'] = [
                {
                    'file': frame.filename.split('/')[-1] if '/' in frame.filename else frame.filename.split('\\')[-1],
                    'line': frame.lineno,
                    'function': frame.name
                }
                for frame in stack_summary[:-2]  # Exclude monitor frames
            ]
        except:
            pass

        return info

    def log_loop_state(self, context: str, level: str = "debug", **kwargs):
        """
        Log current event loop state with context.

        Args:
            context: Description of where this is being called
            level: Log level (debug, info, warning, error)
            **kwargs: Additional context to log
        """
        if not self.enabled:
            return

        try:
            loop_info = self.get_loop_info()
            loop_info['context'] = context
            loop_info.update(kwargs)

            # Store in history
            self.loop_history.append(loop_info)
            if len(self.loop_history) > self.max_history:
                self.loop_history.pop(0)

            # Log based on level
            log_func = getattr(logger, level, logger.debug)
            log_func(
                f"Event loop state: {context}",
                loop_exists=loop_info.get('loop_exists'),
                loop_running=loop_info.get('loop_running'),
                loop_closed=loop_info.get('loop_closed'),
                thread=loop_info.get('thread_name'),
                caller=loop_info.get('caller_info'),
                **kwargs
            )

        except Exception as e:
            # Never fail, just log the monitoring error
            logger.debug(f"Event loop monitoring error: {e}")

    def check_loop_conflict(self) -> Optional[Dict[str, Any]]:
        """
        Check if there's a potential event loop conflict.

        Returns:
            Conflict information if detected, None otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Check if we're trying to run another loop
                return {
                    'conflict_type': 'running_loop_exists',
                    'loop_id': id(loop),
                    'thread': threading.current_thread().name,
                    'recommendation': 'Use asyncio.create_task() or nest_asyncio'
                }
        except RuntimeError as e:
            if "There is no current event loop" in str(e):
                return {
                    'conflict_type': 'no_loop_in_thread',
                    'thread': threading.current_thread().name,
                    'recommendation': 'Create new loop with asyncio.new_event_loop()'
                }
        except:
            pass

        return None

    def get_history_summary(self) -> Dict[str, Any]:
        """
        Get summary of loop history for debugging.

        Returns:
            Summary statistics
        """
        if not self.loop_history:
            return {'history_empty': True}

        running_count = sum(1 for h in self.loop_history if h.get('loop_running'))
        unique_loops = len(set(h.get('loop_id') for h in self.loop_history if h.get('loop_id')))
        unique_threads = len(set(h.get('thread_name') for h in self.loop_history))

        return {
            'total_checks': len(self.loop_history),
            'running_loops_seen': running_count,
            'unique_loop_ids': unique_loops,
            'unique_threads': unique_threads,
            'last_check': self.loop_history[-1] if self.loop_history else None
        }


# Global monitor instance
_monitor = EventLoopMonitor()


def monitor_event_loop(context: Optional[str] = None):
    """
    Decorator to monitor event loop state at function entry and exit.

    Args:
        context: Optional context description

    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Log on entry
            func_context = context or f"{func.__module__}.{func.__name__}"
            _monitor.log_loop_state(
                f"Entering {func_context}",
                level="debug",
                function=func.__name__
            )

            # Check for conflicts
            conflict = _monitor.check_loop_conflict()
            if conflict:
                _monitor.log_loop_state(
                    f"Loop conflict detected in {func_context}",
                    level="warning",
                    conflict=conflict
                )

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Log on exit
                _monitor.log_loop_state(
                    f"Exiting {func_context}",
                    level="debug",
                    function=func.__name__
                )

                return result

            except Exception as e:
                # Log on error
                _monitor.log_loop_state(
                    f"Error in {func_context}",
                    level="error",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Log on entry
            func_context = context or f"{func.__module__}.{func.__name__}"
            _monitor.log_loop_state(
                f"Entering async {func_context}",
                level="debug",
                function=func.__name__,
                is_coroutine=True
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Log on exit
                _monitor.log_loop_state(
                    f"Exiting async {func_context}",
                    level="debug",
                    function=func.__name__,
                    is_coroutine=True
                )

                return result

            except Exception as e:
                # Log on error
                _monitor.log_loop_state(
                    f"Error in async {func_context}",
                    level="error",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__,
                    is_coroutine=True
                )
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_loop_state(context: str, **kwargs):
    """
    Convenience function to log loop state.

    Args:
        context: Context description
        **kwargs: Additional context
    """
    _monitor.log_loop_state(context, **kwargs)


def check_loop_conflict() -> Optional[Dict[str, Any]]:
    """
    Check for event loop conflicts.

    Returns:
        Conflict information if detected
    """
    return _monitor.check_loop_conflict()


def get_loop_summary() -> Dict[str, Any]:
    """
    Get summary of event loop monitoring.

    Returns:
        Summary dictionary
    """
    current_state = _monitor.get_loop_info()
    history_summary = _monitor.get_history_summary()

    return {
        'current_state': current_state,
        'history': history_summary,
        'monitoring_enabled': _monitor.enabled
    }


def enable_monitoring(enabled: bool = True):
    """
    Enable or disable monitoring.

    Args:
        enabled: Whether to enable monitoring
    """
    _monitor.enabled = enabled
    logger.info(f"Event loop monitoring {'enabled' if enabled else 'disabled'}")


# Specific monitors for critical points
@monitor_event_loop("Celery Worker Task")
def monitor_celery_task(func):
    """Monitor Celery task execution."""
    return func


@monitor_event_loop("OpenAI Analyzer")
def monitor_analyzer(func):
    """Monitor OpenAI analyzer calls."""
    return func


@monitor_event_loop("Parallel Processor")
def monitor_parallel_processor(func):
    """Monitor parallel processor execution."""
    return func