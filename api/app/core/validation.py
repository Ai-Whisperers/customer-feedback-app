"""
Core validation logic for feedback data.
Pure functions for data validation and normalization.
"""

from typing import List, Optional
import pandas as pd
import structlog

logger = structlog.get_logger()


def validate_required_columns(df: pd.DataFrame) -> List[str]:
    """
    Validate that required columns are present in the dataframe.

    Args:
        df: Input dataframe

    Returns:
        List of missing column names
    """
    required_columns = ['Nota', 'Comentario Final']
    missing_columns = [col for col in required_columns if col not in df.columns]
    return missing_columns


def validate_rating_range(rating: int) -> bool:
    """
    Validate that a rating is within valid range.

    Args:
        rating: Rating value

    Returns:
        True if valid, False otherwise
    """
    return 0 <= rating <= 10


def validate_comment_length(comment: str, min_length: int = 3) -> bool:
    """
    Validate that a comment meets minimum length requirement.

    Args:
        comment: Comment text
        min_length: Minimum required length

    Returns:
        True if valid, False otherwise
    """
    return len(str(comment).strip()) >= min_length


def normalize_text(text: str) -> str:
    """
    Normalize text by stripping whitespace and converting to string.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    return str(text).strip()


def normalize_feedback_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and clean feedback data.

    Args:
        df: Input dataframe

    Returns:
        Cleaned and normalized dataframe
    """
    # Create a copy to avoid modifying original
    df_clean = df.copy()

    # Clean text
    df_clean['Comentario Final'] = df_clean['Comentario Final'].apply(normalize_text)

    # Filter valid ratings
    df_clean = df_clean[df_clean['Nota'].apply(validate_rating_range)]

    # Filter valid comments
    df_clean = df_clean[df_clean['Comentario Final'].apply(validate_comment_length)]

    # Calculate NPS if not present
    if 'NPS' not in df_clean.columns:
        df_clean['NPS'] = df_clean['Nota'].apply(calculate_nps_category)

    # Reset index
    df_clean = df_clean.reset_index(drop=True)

    logger.info(
        "Data normalization completed",
        original_rows=len(df),
        cleaned_rows=len(df_clean),
        filtered_rows=len(df) - len(df_clean)
    )

    return df_clean


def calculate_nps_category(rating: int) -> str:
    """
    Calculate NPS category from rating.

    Args:
        rating: Rating value (0-10)

    Returns:
        NPS category string
    """
    if rating <= 6:
        return "detractor"
    elif rating <= 8:
        return "passive"
    else:
        return "promoter"


def detect_dominant_language(sample_comments: List[str]) -> Optional[str]:
    """
    Detect dominant language from sample comments.

    Args:
        sample_comments: List of sample comments

    Returns:
        Language code ('es' or 'en') or None
    """
    if not sample_comments:
        return None

    spanish_indicators = ['ñ', 'á', 'é', 'í', 'ó', 'ú']
    spanish_words = ['el', 'la', 'de', 'que', 'en', 'por', 'un', 'con']

    spanish_score = 0
    total_comments = len(sample_comments)

    for comment in sample_comments:
        comment_lower = comment.lower()

        # Check for Spanish characters
        if any(char in comment_lower for char in spanish_indicators):
            spanish_score += 2

        # Check for Spanish words
        words = comment_lower.split()
        spanish_word_count = sum(1 for word in spanish_words if word in words)
        if spanish_word_count >= 2:
            spanish_score += 1

    # If >60% comments seem Spanish, return Spanish hint
    if spanish_score / total_comments > 0.6:
        return "es"
    else:
        return "en"