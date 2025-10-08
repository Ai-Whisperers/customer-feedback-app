"""
OpenAI-specific logging utilities.
Captures detailed metrics for API calls including tokens, rate limits, and response integrity.
"""

import time
import json
import functools
from typing import Dict, Any, Optional, Callable, Tuple
import structlog
from openai import AsyncOpenAI
import asyncio

logger = structlog.get_logger()


class OpenAIMetricsCollector:
    """Collects and logs detailed OpenAI API metrics."""
    
    def __init__(self):
        self.metrics = {
            'total_requests': 0,
            'total_tokens': 0,
            'truncated_responses': 0,
            'rate_limit_hits': 0,
            'average_response_time': 0,
            'batch_failures': {}
        }
    
    def log_request_start(
        self,
        batch_index: int,
        comment_count: int,
        prompt_length: int
    ) -> Dict[str, Any]:
        """Log the start of an OpenAI request."""
        context = {
            'batch_index': batch_index,
            'comment_count': comment_count,
            'prompt_chars': prompt_length,
            'estimated_tokens': prompt_length // 4,  # Rough estimate
            'timestamp': time.time()
        }
        
        logger.info(
            "OpenAI request started",
            **context
        )
        
        return context
    
    def log_response_details(
        self,
        context: Dict[str, Any],
        response: Any,
        response_text: str,
        is_complete: bool
    ) -> None:
        """Log detailed response information."""
        duration = time.time() - context['timestamp']

        # Extract token usage from response
        usage = getattr(response, 'usage', None)
        tokens_used = {
            'prompt_tokens': usage.prompt_tokens if usage else 0,
            'completion_tokens': usage.completion_tokens if usage else 0,
            'total_tokens': usage.total_tokens if usage else 0
        }

        # Check if response is truncated
        is_truncated = not is_complete or response_text.endswith('...')
        if response.choices and response.choices[0].finish_reason:
            finish_reason = response.choices[0].finish_reason
            is_truncated = is_truncated or finish_reason == 'length'
        else:
            finish_reason = 'unknown'

        # Extract rate limit info from response headers (if available)
        rate_limit_info = self._extract_rate_limits(response)

        # Calculate response metrics
        response_metrics = {
            'batch_index': context['batch_index'],
            'duration_seconds': round(duration, 3),
            'response_length': len(response_text),
            'tokens': tokens_used,
            'finish_reason': finish_reason,
            'is_truncated': is_truncated,
            'is_complete_json': self._is_valid_json(response_text),
            'rate_limits': rate_limit_info,
            'tokens_per_comment': round(tokens_used['total_tokens'] / context['comment_count'], 2) if context['comment_count'] > 0 else 0
        }

        # Update global metrics
        self.metrics['total_requests'] += 1
        self.metrics['total_tokens'] += tokens_used['total_tokens']
        if is_truncated:
            self.metrics['truncated_responses'] += 1

        # Update MetricsService (for persistence and dashboard)
        try:
            from app.services.metrics_service import MetricsService
            MetricsService.update_global_metrics(
                prompt_tokens=tokens_used['prompt_tokens'],
                completion_tokens=tokens_used['completion_tokens'],
                total_tokens=tokens_used['total_tokens'],
                comments_processed=context['comment_count'],
                batches_processed=1,
                duration_seconds=duration
            )
        except Exception as e:
            logger.warning("Failed to update MetricsService", error=str(e))

        # Log with appropriate level
        if is_truncated:
            logger.warning(
                "OpenAI response truncated",
                **response_metrics
            )
        else:
            logger.info(
                "OpenAI response complete",
                **response_metrics
            )
    
    def log_error(
        self,
        context: Dict[str, Any],
        error: Exception,
        retry_count: int = 0
    ) -> None:
        """Log OpenAI API errors with context."""
        error_details = {
            'batch_index': context['batch_index'],
            'error_type': type(error).__name__,
            'error_message': str(error),
            'retry_count': retry_count,
            'duration': time.time() - context['timestamp']
        }
        
        # Track specific error types
        if 'rate_limit' in str(error).lower():
            self.metrics['rate_limit_hits'] += 1
            error_details['throttled'] = True
        
        # Track batch-specific failures
        batch_idx = context['batch_index']
        if batch_idx not in self.metrics['batch_failures']:
            self.metrics['batch_failures'][batch_idx] = []
        self.metrics['batch_failures'][batch_idx].append(error_details)
        
        logger.error(
            "OpenAI API error",
            **error_details
        )
    
    def log_batch_summary(
        self,
        total_batches: int,
        completed_batches: int,
        failed_batches: list
    ) -> None:
        """Log summary of batch processing."""
        summary = {
            'total_batches': total_batches,
            'completed': completed_batches,
            'failed': len(failed_batches),
            'success_rate': round(completed_batches / total_batches * 100, 2) if total_batches > 0 else 0,
            'failed_indices': failed_batches,
            'total_tokens_used': self.metrics['total_tokens'],
            'truncation_rate': round(self.metrics['truncated_responses'] / total_batches * 100, 2) if total_batches > 0 else 0,
            'rate_limit_hits': self.metrics['rate_limit_hits']
        }
        
        logger.info(
            "Batch processing summary",
            **summary
        )
    
    def _extract_rate_limits(self, response: Any) -> Dict[str, Any]:
        """Extract rate limit information from response headers."""
        # OpenAI SDK doesn't expose headers directly in async mode
        # This would need custom HTTP client to access
        # For now, return placeholder
        return {
            'requests_remaining': 'unknown',
            'tokens_remaining': 'unknown',
            'reset_time': 'unknown'
        }
    
    def _is_valid_json(self, text: str) -> bool:
        """Check if response is valid JSON."""
        try:
            json.loads(text)
            return True
        except:
            return False


def log_openai_call(metrics_collector: Optional[OpenAIMetricsCollector] = None):
    """Decorator to log OpenAI API calls with detailed metrics."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract batch info from arguments
            batch_index = kwargs.get('batch_index', 0)
            comments = args[1] if len(args) > 1 else kwargs.get('comments', [])
            
            # Initialize collector if not provided
            collector = metrics_collector or OpenAIMetricsCollector()
            
            # Calculate prompt size
            prompt_length = sum(len(c) for c in comments) if comments else 0
            
            # Log start
            context = collector.log_request_start(
                batch_index=batch_index,
                comment_count=len(comments),
                prompt_length=prompt_length
            )
            
            try:
                # Call the actual function
                result = await func(*args, **kwargs)
                
                # Log success (assuming result contains the response)
                # This would need adjustment based on actual return format
                if isinstance(result, dict) and 'response_text' in result:
                    collector.log_response_details(
                        context=context,
                        response=result.get('response'),
                        response_text=result.get('response_text', ''),
                        is_complete=result.get('is_complete', True)
                    )
                
                return result
                
            except Exception as e:
                # Log error
                retry_count = kwargs.get('retry_count', 0)
                collector.log_error(
                    context=context,
                    error=e,
                    retry_count=retry_count
                )
                raise
        
        return wrapper
    return decorator


class ResponseValidator:
    """Validates and attempts to repair OpenAI responses."""
    
    @staticmethod
    def validate_and_repair(response_text: str, expected_count: int) -> Tuple[str, bool, list]:
        """
        Validate response and attempt repairs if needed.
        
        Returns:
            Tuple of (repaired_text, is_valid, issues_found)
        """
        issues = []
        
        # Check if JSON is complete
        if not response_text.strip().endswith('}'):
            issues.append('incomplete_json')
            # Attempt to close JSON
            response_text = ResponseValidator._attempt_json_closure(response_text)
        
        # Validate JSON structure
        try:
            data = json.loads(response_text)
            
            # Check if we have the expected structure
            if 'r' not in data:
                issues.append('missing_r_key')
                return response_text, False, issues
            
            # Check array count
            actual_count = len(data['r'])
            if actual_count < expected_count:
                issues.append(f'incomplete_results: {actual_count}/{expected_count}')
                
                # Log which indices are missing
                logger.warning(
                    "Incomplete batch results",
                    expected=expected_count,
                    received=actual_count,
                    completion_rate=round(actual_count/expected_count*100, 2)
                )
            
            return response_text, len(issues) == 0, issues
            
        except json.JSONDecodeError as e:
            issues.append(f'json_error: {str(e)}')
            
            # Attempt recovery
            repaired = ResponseValidator._attempt_recovery(response_text, expected_count)
            if repaired != response_text:
                try:
                    json.loads(repaired)
                    issues.append('recovered')
                    return repaired, False, issues
                except:
                    pass
            
            return response_text, False, issues
    
    @staticmethod
    def _attempt_json_closure(text: str) -> str:
        """Attempt to properly close incomplete JSON."""
        # Count open brackets
        open_brackets = text.count('{') - text.count('}')
        open_squares = text.count('[') - text.count(']')
        
        # Add missing closures
        if text.rstrip().endswith(','):
            text = text.rstrip()[:-1]  # Remove trailing comma
        
        # Close any open strings
        if text.count('"') % 2 != 0:
            text += '"'
        
        # Close arrays and objects
        text += ']' * open_squares
        text += '}' * open_brackets
        
        return text
    
    @staticmethod
    def _attempt_recovery(text: str, expected_count: int) -> str:
        """Attempt to recover partial valid data."""
        # Try to find the last complete item
        try:
            # Find last complete array item
            last_complete = text.rfind('},{')
            if last_complete > 0:
                # Truncate to last complete item and close
                truncated = text[:last_complete + 1]
                truncated = ResponseValidator._attempt_json_closure(truncated)
                
                logger.info(
                    "Attempted response recovery",
                    original_length=len(text),
                    recovered_length=len(truncated)
                )
                
                return truncated
        except:
            pass
        
        return text


# Global metrics collector instance
global_metrics = OpenAIMetricsCollector()
