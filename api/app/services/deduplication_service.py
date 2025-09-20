"""
Deduplication service for comment similarity detection.
Uses fuzzy matching to identify and map duplicate comments.
"""

import hashlib
from typing import List, Tuple, Dict, Optional
from difflib import SequenceMatcher
import structlog

logger = structlog.get_logger()


class DeduplicationService:
    """Service for detecting and mapping duplicate comments."""

    def __init__(self, threshold: float = 0.85):
        """
        Initialize deduplication service.
        
        Args:
            threshold: Similarity threshold (0-1) for considering duplicates
        """
        self.threshold = threshold
        self.cache = {}  # Cache for similarity comparisons

    def find_duplicates(
        self, 
        comments: List[str]
    ) -> Tuple[List[int], Dict[int, int]]:
        """
        Find unique comments and map duplicates to their originals.
        
        Args:
            comments: List of comment strings
            
        Returns:
            Tuple of:
                - List of unique comment indices
                - Dict mapping duplicate indices to their original index
        """
        unique_indices = []
        duplicate_map = {}
        processed_hashes = {}
        
        logger.info(
            "Starting deduplication",
            total_comments=len(comments),
            threshold=self.threshold
        )
        
        for i, comment in enumerate(comments):
            # Skip empty or very short comments
            if not comment or len(comment.strip()) < 5:
                unique_indices.append(i)
                continue
                
            # Normalize for comparison
            normalized = self._normalize_comment(comment)
            comment_hash = self._get_hash(normalized)
            
            # Check exact match first (via hash)
            if comment_hash in processed_hashes:
                duplicate_map[i] = processed_hashes[comment_hash]
                continue
            
            # Check fuzzy match with existing unique comments
            is_duplicate = False
            for unique_idx in unique_indices:
                if self._is_similar(
                    normalized, 
                    self._normalize_comment(comments[unique_idx])
                ):
                    duplicate_map[i] = unique_idx
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_indices.append(i)
                processed_hashes[comment_hash] = i
        
        logger.info(
            "Deduplication completed",
            unique_count=len(unique_indices),
            duplicate_count=len(duplicate_map),
            reduction_pct=round(len(duplicate_map) / len(comments) * 100, 1)
        )
        
        return unique_indices, duplicate_map

    def _normalize_comment(self, comment: str) -> str:
        """
        Normalize comment for comparison.
        
        Args:
            comment: Original comment text
            
        Returns:
            Normalized comment
        """
        # Convert to lowercase, strip whitespace, remove extra spaces
        normalized = comment.lower().strip()
        normalized = ' '.join(normalized.split())
        
        # Remove common trivial variations
        replacements = [
            ('.', ''),
            (',', ''),
            ('!', ''),
            ('?', ''),
            ('"', ''),
            ("'", ''),
            ('todo bien', 'bien'),
            ('muy bien', 'bien'),
            ('todo mal', 'mal'),
            ('muy mal', 'mal'),
            ('excelente servicio', 'excelente'),
            ('pesimo servicio', 'pesimo'),
            ('mal servicio', 'mal'),
            ('buen servicio', 'bien')
        ]
        
        for old, new in replacements:
            normalized = normalized.replace(old, new)
        
        return normalized

    def _get_hash(self, text: str) -> str:
        """
        Get hash of text for exact matching.
        
        Args:
            text: Text to hash
            
        Returns:
            Hash string
        """
        return hashlib.md5(text.encode()).hexdigest()

    def _is_similar(self, text1: str, text2: str) -> bool:
        """
        Check if two texts are similar based on threshold.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            True if similarity >= threshold
        """
        # Use cache to avoid recalculating
        cache_key = (text1, text2) if text1 < text2 else (text2, text1)
        
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Calculate similarity
        similarity = SequenceMatcher(None, text1, text2).ratio()
        result = similarity >= self.threshold
        
        # Cache result
        self.cache[cache_key] = result
        
        return result


def filter_trivial_comments(
    comments: List[str], 
    indices: Optional[List[int]] = None
) -> List[int]:
    """
    Filter out trivial comments that don't need analysis.
    
    Args:
        comments: List of all comments
        indices: Optional list of indices to check (defaults to all)
        
    Returns:
        List of non-trivial comment indices
    """
    TRIVIAL_PATTERNS = {
        'ok', 'bien', 'mal', 'regular', '.', '...', '.',
        'si', 'no', 'gracias', 'nada', 'todo bien',
        'sin comentarios', 'n/a', '-', 'na', 'ninguno',
        'perfecto', 'excelente', 'pesimo', 'horrible',
        'bueno', 'malo', 'normal', '👍', '👎', 'x'
    }
    
    if indices is None:
        indices = list(range(len(comments)))
    
    filtered = []
    trivial_count = 0
    
    for idx in indices:
        comment = comments[idx].strip().lower()
        
        # Check length
        if len(comment) < 10:
            # Check if it's a trivial pattern
            if comment in TRIVIAL_PATTERNS:
                trivial_count += 1
                continue
        
        # Check if it's just punctuation or numbers
        if all(c in '.,!?;:-1234567890 ' for c in comment):
            trivial_count += 1
            continue
        
        filtered.append(idx)
    
    if trivial_count > 0:
        logger.info(
            "Filtered trivial comments",
            filtered_count=trivial_count,
            remaining=len(filtered)
        )
    
    return filtered
