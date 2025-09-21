"""
Flexible file parser module with dynamic column detection.
Supports chunked reading, column mapping, and intelligent detection.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
import pandas as pd
import structlog

from .file_parser import BaseFileParser

logger = structlog.get_logger()


class FlexibleFileParser(BaseFileParser):
    """Flexible parser with dynamic column detection and mapping."""

    # Column mapping patterns for flexible detection
    COLUMN_MAPPINGS = {
        'nota': {
            'patterns': [r'nota', r'rating', r'score', r'calificaci[oó]n', r'puntuaci[oó]n'],
            'target': 'Nota'
        },
        'comentario': {
            'patterns': [
                r'comentario.*final', r'feedback', r'comment',
                r'observaci[oó]n', r'retroalimentaci[oó]n', r'mensaje'
            ],
            'target': 'Comentario Final'
        },
        'nps': {
            'patterns': [r'nps', r'net.*promoter', r'promotor.*neto'],
            'target': 'NPS'
        }
    }

    def __init__(self, encoding: str = 'utf-8', chunk_size: Optional[int] = None):
        """
        Initialize flexible parser.

        Args:
            encoding: File encoding to use
            chunk_size: Chunk size for reading large files (rows per chunk)
        """
        super().__init__(encoding)
        self.chunk_size = chunk_size or int(os.getenv('PARSER_CHUNK_SIZE', '10000'))

    def parse_file(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parse file with flexible column detection.

        Args:
            file_path: Path to the file to parse

        Returns:
            Tuple of (DataFrame, metadata dict)
        """
        logger.info("Starting flexible file parsing", file_path=str(file_path))

        # Detect columns first
        detected_columns = self._detect_columns(file_path)

        # Read file with detected mappings
        df = self._read_file_with_mapping(file_path, detected_columns)

        # Validate structure with flexible columns
        validation_result = self._validate_flexible_structure(df, detected_columns)
        if not validation_result['valid']:
            raise ValueError(validation_result['error'])

        # Normalize column names to expected format
        df = self._normalize_column_names(df, detected_columns)

        # Normalize data types
        df = self._normalize_data_types(df)

        # Detect NPS handling strategy
        nps_strategy = self._detect_nps_strategy(df, detected_columns)

        # Build metadata
        metadata = {
            'total_rows': len(df),
            'original_columns': list(detected_columns['original_names']),
            'mapped_columns': list(df.columns),
            'has_nps_column': nps_strategy['has_column'],
            'nps_strategy': nps_strategy['strategy'],
            'file_extension': file_path.suffix.lower(),
            'validation': validation_result,
            'column_mappings': detected_columns['mappings']
        }

        logger.info(
            "Flexible file parsing completed",
            total_rows=metadata['total_rows'],
            nps_strategy=nps_strategy['strategy']
        )

        return df, metadata

    def _detect_columns(self, file_path: Path) -> Dict[str, Any]:
        """
        Detect columns and create mappings.

        Args:
            file_path: Path to the file

        Returns:
            Column detection results
        """
        # Read just the header
        if file_path.suffix.lower() == '.csv':
            df_sample = pd.read_csv(file_path, nrows=5, encoding=self.encoding)
        else:
            df_sample = pd.read_excel(file_path, nrows=5)

        original_columns = list(df_sample.columns)
        mappings = {}
        detected_types = {}

        for col in original_columns:
            col_lower = col.lower().strip()

            # Try to match column patterns
            for field_type, config in self.COLUMN_MAPPINGS.items():
                for pattern in config['patterns']:
                    if re.search(pattern, col_lower):
                        mappings[col] = config['target']
                        detected_types[config['target']] = field_type
                        break
                if col in mappings:
                    break

        # Check if we have minimum required columns
        required_found = all(
            target in mappings.values()
            for target in self.REQUIRED_COLUMNS
        )

        logger.info(
            "Column detection completed",
            original_count=len(original_columns),
            mapped_count=len(mappings),
            required_found=required_found
        )

        return {
            'original_names': original_columns,
            'mappings': mappings,
            'detected_types': detected_types,
            'has_required': required_found
        }

    def _read_file_with_mapping(
        self,
        file_path: Path,
        detected_columns: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Read file with column mapping applied.

        Args:
            file_path: Path to the file
            detected_columns: Detected column information

        Returns:
            DataFrame with mapped columns
        """
        # Determine if we should use chunked reading
        use_chunks = self._should_use_chunks(file_path)

        if use_chunks:
            logger.info("Using chunked reading", chunk_size=self.chunk_size)
            df = self._read_file_chunked(file_path)
        else:
            df = self._read_file(file_path)

        return df

    def _should_use_chunks(self, file_path: Path) -> bool:
        """
        Determine if chunked reading should be used.

        Args:
            file_path: Path to the file

        Returns:
            True if chunks should be used
        """
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        chunk_threshold_mb = float(os.getenv('CHUNK_THRESHOLD_MB', '10'))

        return file_size_mb > chunk_threshold_mb

    def _read_file_chunked(self, file_path: Path) -> pd.DataFrame:
        """
        Read file in chunks.

        Args:
            file_path: Path to the file

        Returns:
            Combined DataFrame
        """
        chunks = []

        if file_path.suffix.lower() == '.csv':
            reader = pd.read_csv(
                file_path,
                encoding=self.encoding,
                chunksize=self.chunk_size
            )
        else:
            # Excel doesn't support chunked reading directly
            return self._read_file(file_path)

        for chunk in reader:
            chunks.append(chunk)

        return pd.concat(chunks, ignore_index=True)

    def _normalize_column_names(
        self,
        df: pd.DataFrame,
        detected_columns: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Normalize column names to expected format.

        Args:
            df: DataFrame with original columns
            detected_columns: Column detection results

        Returns:
            DataFrame with normalized column names
        """
        df_normalized = df.copy()

        # Apply column mappings
        if detected_columns['mappings']:
            df_normalized = df_normalized.rename(columns=detected_columns['mappings'])

        return df_normalized

    def _validate_flexible_structure(
        self,
        df: pd.DataFrame,
        detected_columns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate structure with flexible column detection.

        Args:
            df: DataFrame to validate
            detected_columns: Column detection results

        Returns:
            Validation result
        """
        if not detected_columns['has_required']:
            # Try to find required columns in mapped DataFrame
            missing = []
            for required_col in self.REQUIRED_COLUMNS:
                found = False
                for mapped_col in detected_columns['mappings'].values():
                    if mapped_col == required_col:
                        found = True
                        break
                if not found:
                    missing.append(required_col)

            if missing:
                return {
                    'valid': False,
                    'error': f"Could not detect required columns: {', '.join(missing)}",
                    'missing_columns': missing,
                    'suggestions': self._generate_column_suggestions(detected_columns)
                }

        return {
            'valid': True,
            'error': None,
            'missing_columns': [],
            'detected_mappings': detected_columns['mappings']
        }

    def _generate_column_suggestions(
        self,
        detected_columns: Dict[str, Any]
    ) -> List[str]:
        """
        Generate suggestions for missing columns.

        Args:
            detected_columns: Column detection results

        Returns:
            List of suggestions
        """
        suggestions = []

        if 'Nota' not in detected_columns['mappings'].values():
            suggestions.append(
                "Add a column with ratings (0-10) named: 'Nota', 'Rating', "
                "'Calificación', or 'Score'"
            )

        if 'Comentario Final' not in detected_columns['mappings'].values():
            suggestions.append(
                "Add a column with feedback text named: 'Comentario Final', "
                "'Feedback', 'Comment', or 'Observación'"
            )

        return suggestions

    def _detect_nps_strategy(
        self,
        df: pd.DataFrame,
        detected_columns: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect NPS handling strategy.

        Args:
            df: DataFrame with data
            detected_columns: Column detection results

        Returns:
            NPS strategy information
        """
        has_nps_column = 'NPS' in df.columns
        strategy = 'existing' if has_nps_column else 'calculated'

        if has_nps_column:
            # Analyze NPS column content
            nps_sample = df['NPS'].dropna().head(100)

            if pd.api.types.is_numeric_dtype(nps_sample):
                # Numeric NPS values
                if nps_sample.between(-100, 100).all():
                    strategy = 'existing_score'
                elif nps_sample.between(0, 10).all():
                    strategy = 'existing_rating'
            else:
                # Text NPS categories
                nps_categories = set(nps_sample.astype(str).str.lower())
                expected_categories = {'promoter', 'passive', 'detractor',
                                      'promotor', 'pasivo', 'detractor'}

                if nps_categories.issubset(expected_categories):
                    strategy = 'existing_category'

        return {
            'has_column': has_nps_column,
            'strategy': strategy,
            'needs_calculation': strategy == 'calculated'
        }

    def validate_data_quality_flexible(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Enhanced data quality validation with flexible detection.

        Args:
            df: DataFrame to validate

        Returns:
            Enhanced quality statistics
        """
        base_stats = self.validate_data_quality(df)

        # Add NPS-specific validation
        if 'NPS' in df.columns:
            nps_stats = self._validate_nps_data(df['NPS'])
            base_stats['nps_validation'] = nps_stats

        # Add text quality metrics
        if 'Comentario Final' in df.columns:
            text_stats = self._analyze_text_quality(df['Comentario Final'])
            base_stats['text_quality'] = text_stats

        return base_stats

    def _validate_nps_data(self, nps_series: pd.Series) -> Dict[str, Any]:
        """
        Validate NPS data quality.

        Args:
            nps_series: Series with NPS data

        Returns:
            NPS validation statistics
        """
        nps_clean = nps_series.dropna()

        if len(nps_clean) == 0:
            return {'valid': False, 'reason': 'No NPS data found'}

        if pd.api.types.is_numeric_dtype(nps_clean):
            return {
                'valid': True,
                'type': 'numeric',
                'range': [nps_clean.min(), nps_clean.max()],
                'mean': nps_clean.mean()
            }
        else:
            categories = nps_clean.astype(str).str.lower().value_counts()
            return {
                'valid': True,
                'type': 'categorical',
                'categories': categories.to_dict()
            }

    def _analyze_text_quality(self, text_series: pd.Series) -> Dict[str, Any]:
        """
        Analyze text quality metrics.

        Args:
            text_series: Series with text data

        Returns:
            Text quality statistics
        """
        text_clean = text_series.dropna()

        return {
            'total_comments': len(text_clean),
            'avg_length': text_clean.str.len().mean(),
            'min_length': text_clean.str.len().min(),
            'max_length': text_clean.str.len().max(),
            'empty_count': (text_clean.str.strip() == '').sum(),
            'language_detected': self._detect_predominant_language(text_clean)
        }

    def _detect_predominant_language(self, text_series: pd.Series) -> str:
        """
        Detect predominant language in text.

        Args:
            text_series: Series with text data

        Returns:
            Language code (es/en/mixed)
        """
        # Simple heuristic based on common words
        spanish_words = {'el', 'la', 'de', 'que', 'y', 'en', 'es', 'por', 'con'}
        english_words = {'the', 'is', 'and', 'to', 'of', 'in', 'for', 'with', 'it'}

        sample_text = ' '.join(text_series.head(100).astype(str)).lower()
        words = set(sample_text.split())

        spanish_count = len(words.intersection(spanish_words))
        english_count = len(words.intersection(english_words))

        if spanish_count > english_count * 2:
            return 'es'
        elif english_count > spanish_count * 2:
            return 'en'
        else:
            return 'mixed'