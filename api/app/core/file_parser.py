"""
File parser module with base parsing functionality.
Handles Excel and CSV file parsing with validation.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import structlog

logger = structlog.get_logger()


class BaseFileParser:
    """Base parser with mechanical parsing logic."""

    REQUIRED_COLUMNS = ['Nota', 'Comentario Final']
    OPTIONAL_COLUMNS = ['NPS']

    def __init__(self, encoding: str = 'utf-8'):
        """
        Initialize base parser.

        Args:
            encoding: File encoding to use
        """
        self.encoding = encoding

    def parse_file(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse file and return DataFrame with metadata.

        Args:
            file_path: Path to the file to parse

        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        logger.info("Starting file parsing", file_path=str(file_path))

        # Read file based on extension
        df = self._read_file(file_path)

        # Validate structure
        validation_result = self._validate_structure(df)
        if not validation_result['valid']:
            raise ValueError(validation_result['error'])

        # Normalize data types
        df = self._normalize_data_types(df)

        # Detect NPS column
        has_nps_column = 'NPS' in df.columns

        # Build metadata
        metadata = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'has_nps_column': has_nps_column,
            'file_extension': file_path.suffix.lower(),
            'validation': validation_result
        }

        logger.info(
            "File parsing completed",
            total_rows=metadata['total_rows'],
            has_nps=has_nps_column
        )

        return df, metadata

    def _read_file(self, file_path: Path) -> pd.DataFrame:
        """
        Read file based on extension.

        Args:
            file_path: Path to the file

        Returns:
            DataFrame with file contents
        """
        try:
            if file_path.suffix.lower() == '.csv':
                return pd.read_csv(file_path, encoding=self.encoding)
            else:
                return pd.read_excel(file_path)
        except Exception as e:
            logger.error("Failed to read file", error=str(e))
            raise ValueError(f"Failed to read file: {str(e)}")

    def _validate_structure(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate DataFrame structure.

        Args:
            df: DataFrame to validate

        Returns:
            Validation result dictionary
        """
        missing_columns = [
            col for col in self.REQUIRED_COLUMNS
            if col not in df.columns
        ]

        if missing_columns:
            return {
                'valid': False,
                'error': f"Missing required columns: {', '.join(missing_columns)}",
                'missing_columns': missing_columns,
                'found_columns': list(df.columns)
            }

        return {
            'valid': True,
            'error': None,
            'missing_columns': [],
            'found_columns': list(df.columns)
        }

    def _normalize_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize data types for required columns.

        Args:
            df: DataFrame to normalize

        Returns:
            Normalized DataFrame
        """
        df_normalized = df.copy()

        # Normalize Nota column
        if 'Nota' in df_normalized.columns:
            df_normalized['Nota'] = pd.to_numeric(
                df_normalized['Nota'],
                errors='coerce'
            )

        # Normalize Comentario Final column
        if 'Comentario Final' in df_normalized.columns:
            df_normalized['Comentario Final'] = (
                df_normalized['Comentario Final']
                .astype(str)
                .str.strip()
            )

        # Normalize NPS column if present
        if 'NPS' in df_normalized.columns:
            # Try to convert to numeric first
            nps_numeric = pd.to_numeric(df_normalized['NPS'], errors='coerce')

            # If numeric conversion successful, keep numeric values
            # Otherwise, keep as string for category detection
            if nps_numeric.notna().sum() > 0:
                df_normalized['NPS'] = nps_numeric
            else:
                df_normalized['NPS'] = df_normalized['NPS'].astype(str).str.lower()

        return df_normalized

    def validate_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Validate data quality and return statistics.

        Args:
            df: DataFrame to validate

        Returns:
            Data quality statistics
        """
        stats = {
            'total_rows': len(df),
            'valid_rows': 0,
            'invalid_rows': 0,
            'issues': []
        }

        # Check Nota values
        if 'Nota' in df.columns:
            valid_ratings = df['Nota'].notna() & df['Nota'].between(0, 10)
            invalid_rating_count = (~valid_ratings).sum()
            if invalid_rating_count > 0:
                stats['issues'].append(
                    f"{invalid_rating_count} rows with invalid ratings"
                )

        # Check Comentario Final values
        if 'Comentario Final' in df.columns:
            valid_comments = (
                df['Comentario Final'].notna() &
                (df['Comentario Final'].str.len() >= 3)
            )
            invalid_comment_count = (~valid_comments).sum()
            if invalid_comment_count > 0:
                stats['issues'].append(
                    f"{invalid_comment_count} rows with invalid comments"
                )

            # Calculate valid rows (both conditions must be met)
            if 'Nota' in df.columns:
                valid_rows_mask = valid_ratings & valid_comments
                stats['valid_rows'] = valid_rows_mask.sum()
                stats['invalid_rows'] = (~valid_rows_mask).sum()

        return stats


def get_parser(mode: Optional[str] = None) -> BaseFileParser:
    """
    Get parser instance based on mode.

    Args:
        mode: Parser mode (base, flexible, or from env)

    Returns:
        Parser instance
    """
    if mode is None:
        mode = os.getenv('FILE_PARSER_MODE', 'base')

    if mode == 'flexible':
        # Import flexible parser when available
        try:
            from .flexible_parser import FlexibleFileParser
            return FlexibleFileParser()
        except ImportError:
            logger.warning("Flexible parser not available, using base parser")
            return BaseFileParser()
    else:
        return BaseFileParser()