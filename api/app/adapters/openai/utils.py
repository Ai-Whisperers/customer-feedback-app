"""
Utility functions for OpenAI adapter.
"""

from typing import List
import structlog

from app.config import settings

logger = structlog.get_logger()


def format_comments_for_analysis(comments: List[str]) -> str:
    """
    Format comments for analysis input.

    Args:
        comments: List of comment strings

    Returns:
        Formatted string for API input
    """
    formatted = []
    for idx, comment in enumerate(comments):
        formatted.append(f"[{idx}] {comment}")
    return "\n\n".join(formatted)


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough estimation: 1 token ≈ 4 characters for Spanish/English
    return len(text) // 4


def optimize_batch_size(
    comments: List[str],
    max_tokens: int = 3500
) -> List[List[str]]:
    """
    Optimize batch sizes based on token estimates.

    Args:
        comments: List of comments to batch
        max_tokens: Maximum tokens per batch

    Returns:
        List of comment batches
    """
    batches = []
    current_batch = []
    current_tokens = 0

    # Reserve tokens for instructions and response
    available_tokens = max_tokens - 1000

    for comment in comments:
        comment_tokens = estimate_tokens(comment)

        # If adding this comment would exceed the limit, start new batch
        if (current_tokens + comment_tokens > available_tokens and
            len(current_batch) > 0):
            batches.append(current_batch)
            current_batch = [comment]
            current_tokens = comment_tokens
        else:
            current_batch.append(comment)
            current_tokens += comment_tokens

        # Hard limit on batch size
        if len(current_batch) >= settings.MAX_BATCH_SIZE:
            batches.append(current_batch)
            current_batch = []
            current_tokens = 0

    # Add remaining comments
    if current_batch:
        batches.append(current_batch)

    logger.info(
        "Optimized batching",
        total_comments=len(comments),
        total_batches=len(batches),
        avg_batch_size=len(comments) / len(batches) if batches else 0
    )

    return batches