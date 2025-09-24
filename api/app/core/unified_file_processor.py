"""
Unified file processor combining parsing and validation.
Consolidates 3 layers of abstraction into single, clear module.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import pandas as pd
import numpy as np
import structlog
from datetime import datetime

logger = structlog.get_logger()


class UnifiedFileProcessor:
    """
    Single file processor handling both parsing and validation.
    Replaces BaseFileParser, FlexibleFileParser, and scattered validation.
    """

    # Required columns with flexible name mapping
    COLUMN_MAPPINGS = {
        'Nota': ['nota', 'rating', 'score', 'calificacion', 'calificación', 'puntuacion'],
        'Comentario Final': ['comentario', 'comment', 'comentario_final', 'feedback',
                            'comentarios', 'texto', 'respuesta', 'observaciones'],
        'NPS': ['nps', 'nps_score', 'net_promoter_score']
    }

    REQUIRED_COLUMNS = ['Nota', 'Comentario Final']
    OPTIONAL_COLUMNS = ['NPS']

    def __init__(self):
        """Initialize processor with default settings."""
        self.min_comment_length = 3
        self.max_comment_length = 2000
        self.valid_rating_range = (0, 10)

    def process_file(
        self,
        file_path: Path,
        validate_only: bool = False
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Process file with integrated parsing and validation.

        Args:
            file_path: Path to file
            validate_only: If True, only validate without processing

        Returns:
            Tuple of (processed DataFrame, metadata)
        """
        start_time = datetime.now()
        logger.info(f"Processing file: {file_path}")

        # Step 1: Read file
        df = self._read_file(file_path)

        # Step 2: Map columns to standard names
        df = self._map_columns(df)

        # Step 3: Validate structure
        validation_errors = self._validate_structure(df)
        if validation_errors:
            raise ValueError(f"Validation failed: {'; '.join(validation_errors)}")

        if validate_only:
            return df, {"validated": True, "row_count": len(df)}

        # Step 4: Clean and normalize data
        df = self._normalize_data(df)

        # Step 5: Validate data quality
        df = self._validate_data_quality(df)

        # Step 6: Calculate derived fields
        df = self._add_derived_fields(df)

        # Build metadata
        processing_time = (datetime.now() - start_time).total_seconds()
        metadata = self._build_metadata(df, file_path, processing_time)

        logger.info(
            "File processed successfully",
            rows=len(df),
            columns=list(df.columns),
            processing_time=processing_time
        )

        return df, metadata

    def _read_file(self, file_path: Path) -> pd.DataFrame:
        """Read file based on extension."""
        extension = file_path.suffix.lower()

        try:
            if extension in ['.xlsx', '.xls']:
                # Try reading Excel file
                df = pd.read_excel(file_path, engine='openpyxl')
            elif extension == '.csv':
                # Try multiple encodings for CSV
                for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode CSV file with any encoding")
            else:
                raise ValueError(f"Unsupported file extension: {extension}")

            if df.empty:
                raise ValueError("File is empty")

            return df

        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            raise ValueError(f"Error reading file: {str(e)}")

    def _map_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map flexible column names to standard names."""
        # Create lowercase mapping for case-insensitive matching
        column_lower = {col.lower().strip(): col for col in df.columns}

        # Map columns
        for standard_name, variations in self.COLUMN_MAPPINGS.items():
            found = False
            for variation in variations:
                if variation.lower() in column_lower:
                    original_name = column_lower[variation.lower()]
                    if original_name != standard_name:
                        df = df.rename(columns={original_name: standard_name})
                        logger.info(f"Mapped column '{original_name}' to '{standard_name}'")
                    found = True
                    break

            if not found and standard_name in self.REQUIRED_COLUMNS:
                # Try fuzzy matching as last resort
                for col in column_lower:
                    if any(part in col for part in variations):
                        original_name = column_lower[col]
                        df = df.rename(columns={original_name: standard_name})
                        logger.info(f"Fuzzy matched column '{original_name}' to '{standard_name}'")
                        found = True
                        break

        return df

    def _validate_structure(self, df: pd.DataFrame) -> List[str]:
        """Validate DataFrame structure."""
        errors = []

        # Check required columns
        missing_columns = [col for col in self.REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            errors.append(f"Missing required columns: {missing_columns}")

        # Check minimum rows
        if len(df) == 0:
            errors.append("No data rows found")

        return errors

    def _normalize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and normalize data."""
        # Drop rows where both required columns are null
        before_count = len(df)
        df = df.dropna(subset=self.REQUIRED_COLUMNS, how='all')
        dropped = before_count - len(df)
        if dropped > 0:
            logger.info(f"Dropped {dropped} rows with missing required data")

        # Normalize Nota column
        if 'Nota' in df.columns:
            # Convert to numeric, coerce errors to NaN
            df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
            # Fill NaN with median or default
            if df['Nota'].notna().any():
                df['Nota'] = df['Nota'].fillna(df['Nota'].median())
            else:
                df['Nota'] = df['Nota'].fillna(5)
            # Ensure integer type
            df['Nota'] = df['Nota'].round().astype(int)

        # Normalize Comentario Final column
        if 'Comentario Final' in df.columns:
            # Convert to string and clean
            df['Comentario Final'] = df['Comentario Final'].astype(str)
            df['Comentario Final'] = df['Comentario Final'].str.strip()
            # Replace 'nan' string with empty
            df['Comentario Final'] = df['Comentario Final'].replace('nan', '')

        # Normalize NPS column if exists
        if 'NPS' in df.columns:
            df['NPS'] = pd.to_numeric(df['NPS'], errors='coerce')

        return df

    def _validate_data_quality(self, df: pd.DataFrame) -> pd.DataFrame:
        """Validate data quality and mark invalid rows."""
        # Validate rating range
        if 'Nota' in df.columns:
            invalid_ratings = (df['Nota'] < self.valid_rating_range[0]) | \
                            (df['Nota'] > self.valid_rating_range[1])
            if invalid_ratings.any():
                logger.warning(f"Found {invalid_ratings.sum()} ratings outside valid range")
                # Clip to valid range
                df['Nota'] = df['Nota'].clip(*self.valid_rating_range)

        # Validate comment length
        if 'Comentario Final' in df.columns:
            df['comment_length'] = df['Comentario Final'].str.len()
            too_short = df['comment_length'] < self.min_comment_length
            too_long = df['comment_length'] > self.max_comment_length

            if too_short.any():
                logger.warning(f"Found {too_short.sum()} comments too short")
                # Mark but don't remove
                df.loc[too_short, 'comment_valid'] = False
            else:
                df['comment_valid'] = True

            if too_long.any():
                logger.warning(f"Found {too_long.sum()} comments too long, truncating")
                df.loc[too_long, 'Comentario Final'] = \
                    df.loc[too_long, 'Comentario Final'].str[:self.max_comment_length]

            # Drop temporary column
            df = df.drop('comment_length', axis=1)

        return df

    def _add_derived_fields(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add calculated fields."""
        # Calculate NPS category from Nota if NPS column doesn't exist
        if 'Nota' in df.columns:
            df['nps_calculated'] = df['Nota'].apply(self._calculate_nps_category)

        # Detect language (sample-based for performance)
        if 'Comentario Final' in df.columns:
            sample_size = min(10, len(df))
            sample_comments = df['Comentario Final'].head(sample_size).tolist()
            dominant_language = self._detect_language(sample_comments)
            df['detected_language'] = dominant_language

        return df

    def _calculate_nps_category(self, rating: int) -> str:
        """Calculate NPS category from rating."""
        if rating >= 9:
            return 'promoter'
        elif rating >= 7:
            return 'passive'
        else:
            return 'detractor'

    def _detect_language(self, comments: List[str]) -> str:
        """Detect dominant language from comments."""
        # Simple heuristic: count Spanish indicators
        spanish_indicators = ['el', 'la', 'de', 'que', 'es', 'en', 'un', 'por', 'con']
        spanish_count = 0
        total_words = 0

        for comment in comments:
            if not comment or len(comment) < 3:
                continue
            words = comment.lower().split()
            total_words += len(words)
            spanish_count += sum(1 for word in words if word in spanish_indicators)

        if total_words > 0:
            spanish_ratio = spanish_count / total_words
            return 'es' if spanish_ratio > 0.1 else 'en'
        return 'es'  # Default to Spanish

    def _build_metadata(
        self,
        df: pd.DataFrame,
        file_path: Path,
        processing_time: float
    ) -> Dict[str, Any]:
        """Build metadata about processed file."""
        return {
            'file_name': file_path.name,
            'file_size_mb': file_path.stat().st_size / (1024 * 1024),
            'total_rows': len(df),
            'valid_rows': len(df[df.get('comment_valid', True) == True]) if 'comment_valid' in df else len(df),
            'columns_found': list(df.columns),
            'has_nps_column': 'NPS' in df.columns,
            'processing_time_seconds': round(processing_time, 2),
            'detected_language': df['detected_language'].iloc[0] if 'detected_language' in df else 'es',
            'nps_distribution': df['nps_calculated'].value_counts().to_dict() if 'nps_calculated' in df else {}
        }

    @staticmethod
    def validate_upload_file(file_content: bytes, filename: str, max_size_mb: int = 20) -> Dict[str, Any]:
        """
        Quick validation for uploaded files without full processing.

        Args:
            file_content: Raw file bytes
            filename: Original filename
            max_size_mb: Maximum file size in MB

        Returns:
            Validation result dict
        """
        # Check file size
        size_mb = len(file_content) / (1024 * 1024)
        if size_mb > max_size_mb:
            return {
                'valid': False,
                'error': f'File too large: {size_mb:.1f}MB (max: {max_size_mb}MB)'
            }

        # Check extension
        extension = Path(filename).suffix.lower()
        if extension not in ['.xlsx', '.xls', '.csv']:
            return {
                'valid': False,
                'error': f'Unsupported file type: {extension}'
            }

        return {
            'valid': True,
            'size_mb': round(size_mb, 2),
            'extension': extension
        }