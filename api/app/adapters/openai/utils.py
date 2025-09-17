"""
Utility functions for OpenAI adapter with improved token counting.
"""

from typing import List, Tuple
import structlog

from app.config import settings

logger = structlog.get_logger()

# Lazy load transformers to avoid import issues
_tokenizer = None

def _get_tokenizer():
    """Get or create the tokenizer instance."""
    global _tokenizer
    if _tokenizer is None:
        try:
            from transformers import GPT2TokenizerFast
            _tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
        except Exception as e:
            logger.warning(f"Failed to load transformers tokenizer: {e}")
            _tokenizer = False  # Mark as failed
    return _tokenizer


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


def count_tokens(text: str, model: str = None) -> int:
    """
    Count actual tokens using transformers for accurate estimation.

    Args:
        text: Input text
        model: Model name (defaults to settings.AI_MODEL)

    Returns:
        Actual token count
    """
    if model is None:
        model = settings.AI_MODEL

    tokenizer = _get_tokenizer()

    if tokenizer and tokenizer is not False:
        try:
            # Use the transformers tokenizer
            tokens = tokenizer.encode(text)
            return len(tokens)
        except Exception as e:
            logger.warning(
                "Failed to count tokens with transformers, using estimation",
                error=str(e)
            )

    # Fallback to rough estimation: ~1 token per 4 characters
    return len(text) // 4


def estimate_tokens(text: str) -> int:
    """
    Quick token estimation without tokenizer (for backwards compatibility).

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    # Rough estimation: 1 token ≈ 4 characters for Spanish/English
    # Slightly more conservative for Spanish (more characters per token)
    return len(text) // 4


def optimize_batch_size(
    comments: List[str],
    max_tokens_per_batch: int = 3000,
    use_accurate_counting: bool = True
) -> List[List[str]]:
    """
    Optimize batch sizes based on token estimates with dynamic sizing.

    Args:
        comments: List of comments to batch
        max_tokens_per_batch: Maximum tokens per batch (input)
        use_accurate_counting: Use tiktoken for accurate counting

    Returns:
        List of comment batches optimized for token usage
    """
    batches = []
    current_batch = []
    current_tokens = 0

    # Reserve tokens for system prompt (~500) and response structure (~1500)
    # This ensures we have enough space for the full response
    reserved_tokens = 2000
    available_tokens = max_tokens_per_batch - reserved_tokens

    # Token counting function (use transformers if available)
    count_fn = count_tokens if use_accurate_counting else estimate_tokens

    # Pre-calculate token counts for all comments
    comment_tokens = []
    for comment in comments:
        # Truncate very long comments to prevent single comment from exceeding limit
        truncated = comment[:1500] if len(comment) > 1500 else comment
        tokens = count_fn(truncated)
        comment_tokens.append((truncated, tokens))

    logger.info(
        "Token analysis complete",
        total_comments=len(comments),
        total_tokens=sum(t for _, t in comment_tokens),
        avg_tokens_per_comment=sum(t for _, t in comment_tokens) / len(comments) if comments else 0
    )

    # Dynamic batching based on token count
    for comment, tokens in comment_tokens:
        # If single comment exceeds limit, put it in its own batch
        if tokens > available_tokens:
            if current_batch:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0
            batches.append([comment])
            logger.warning(
                "Large comment in single batch",
                tokens=tokens,
                limit=available_tokens
            )
            continue

        # Check if adding this comment would exceed limits
        would_exceed_tokens = current_tokens + tokens > available_tokens
        would_exceed_size = len(current_batch) >= settings.MAX_BATCH_SIZE

        if (would_exceed_tokens or would_exceed_size) and current_batch:
            # Save current batch and start new one
            batches.append(current_batch)
            logger.debug(
                "Created batch",
                batch_size=len(current_batch),
                batch_tokens=current_tokens
            )
            current_batch = [comment]
            current_tokens = tokens
        else:
            # Add to current batch
            current_batch.append(comment)
            current_tokens += tokens

    # Add remaining comments
    if current_batch:
        batches.append(current_batch)
        logger.debug(
            "Created final batch",
            batch_size=len(current_batch),
            batch_tokens=current_tokens
        )

    # Log batching statistics
    batch_sizes = [len(b) for b in batches]
    logger.info(
        "Optimized batching complete",
        total_comments=len(comments),
        total_batches=len(batches),
        batch_sizes=batch_sizes,
        min_batch_size=min(batch_sizes) if batch_sizes else 0,
        max_batch_size=max(batch_sizes) if batch_sizes else 0,
        avg_batch_size=sum(batch_sizes) / len(batch_sizes) if batch_sizes else 0
    )

    return batches


def split_large_batch(
    comments: List[str],
    target_size: int = 30
) -> List[List[str]]:
    """
    Simple split for large batches into fixed sizes.

    Args:
        comments: List of comments
        target_size: Target batch size

    Returns:
        List of batches with target size
    """
    batches = []
    for i in range(0, len(comments), target_size):
        batches.append(comments[i:i + target_size])
    return batches


def calculate_optimal_concurrency(
    total_comments: int,
    max_rps: int = None
) -> Tuple[int, int]:
    """
    Calculate optimal batch size and concurrency for processing.

    Args:
        total_comments: Total number of comments
        max_rps: Maximum requests per second (defaults to settings.MAX_RPS)

    Returns:
        Tuple of (optimal_batch_size, optimal_concurrency)
    """
    if max_rps is None:
        max_rps = settings.MAX_RPS

    # Determine optimal batch size based on total comments
    if total_comments <= 50:
        batch_size = min(25, total_comments)
    elif total_comments <= 200:
        batch_size = 30
    elif total_comments <= 500:
        batch_size = 40
    else:
        batch_size = 50

    # Calculate concurrency based on RPS limit
    # Leave some buffer for rate limiting
    optimal_concurrency = min(
        max_rps * 0.8,  # Use 80% of rate limit
        settings.CELERY_WORKER_CONCURRENCY
    )

    return int(batch_size), int(optimal_concurrency)