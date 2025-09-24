"""
Efficient O(n) deduplication service.
Uses in-memory hash-based approach to avoid Redis memory constraints.
"""

import hashlib
from typing import List, Dict, Tuple, Set
import re
import unicodedata
import structlog

logger = structlog.get_logger()


class EfficientDeduplicationService:
    """
    Fast deduplication using hash-based approach.
    O(n) complexity instead of O(n²).
    """

    def __init__(self):
        # Nothing to persist - each request is independent
        pass

    def deduplicate_comments(
        self,
        comments: List[str],
        ratings: List[int] = None,
        similarity_threshold: float = 0.85
    ) -> Tuple[List[str], List[int], List[int], Dict[int, int], Dict[str, any]]:
        """
        Deduplicate comments efficiently using hash-based exact matching
        and lightweight fuzzy matching.

        Args:
            comments: List of comment strings
            ratings: Optional list of ratings
            similarity_threshold: Similarity threshold (0.85 = 85% similar)

        Returns:
            Tuple of:
            - filtered_comments: Unique comments
            - filtered_ratings: Corresponding ratings
            - filtered_indices: Original indices of unique comments
            - duplicate_map: Map of duplicate index -> original index
            - dedup_info: Statistics about deduplication
        """
        if not comments:
            return [], [], [], {}, {"original_count": 0, "filtered_count": 0}

        # Normalize all comments once
        normalized = [self._normalize_text(c) for c in comments]

        # Phase 1: Exact duplicate detection using hashes - O(n)
        seen_hashes = {}
        seen_normalized = {}
        filtered_comments = []
        filtered_ratings = []
        filtered_indices = []
        duplicate_map = {}

        for idx, (original, normalized_text) in enumerate(zip(comments, normalized)):
            # Calculate hash for exact matching
            text_hash = hashlib.sha256(normalized_text.encode()).hexdigest()

            if text_hash in seen_hashes:
                # Exact duplicate found
                duplicate_map[idx] = seen_hashes[text_hash]
                logger.debug(f"Exact duplicate: {idx} -> {seen_hashes[text_hash]}")
            else:
                # Check for near-duplicates using simplified approach
                # Use first 50 chars as a quick filter
                text_key = normalized_text[:50] if len(normalized_text) > 50 else normalized_text

                is_duplicate = False
                if text_key in seen_normalized:
                    # Potential near-duplicate, do lightweight similarity check
                    similar_indices = seen_normalized[text_key]
                    for similar_idx in similar_indices:
                        if self._quick_similarity(
                            normalized_text,
                            normalized[similar_idx]
                        ) > similarity_threshold:
                            duplicate_map[idx] = similar_idx
                            is_duplicate = True
                            logger.debug(f"Near duplicate: {idx} -> {similar_idx}")
                            break

                if not is_duplicate:
                    # This is a unique comment
                    seen_hashes[text_hash] = idx
                    if text_key not in seen_normalized:
                        seen_normalized[text_key] = []
                    seen_normalized[text_key].append(idx)

                    filtered_comments.append(original)
                    filtered_indices.append(idx)
                    if ratings:
                        filtered_ratings.append(ratings[idx])

        # Phase 2: Filter trivial comments (optional, very fast)
        final_comments = []
        final_ratings = []
        final_indices = []
        trivial_map = {}

        for i, (comment, idx) in enumerate(zip(filtered_comments, filtered_indices)):
            if not self._is_trivial(comment):
                final_comments.append(comment)
                final_indices.append(idx)
                if filtered_ratings:
                    final_ratings.append(filtered_ratings[i])
            else:
                trivial_map[idx] = -1  # Mark as trivial

        # Prepare dedup info
        dedup_info = {
            "original_count": len(comments),
            "filtered_count": len(final_comments),
            "duplicates_removed": len(duplicate_map),
            "trivial_removed": len(trivial_map),
            "all_comments": comments,  # Keep original for expansion later
            "all_ratings": ratings if ratings else [],
            "filtered_indices": final_indices,
            "duplicate_map": duplicate_map
        }

        logger.info(
            "Deduplication complete",
            original=len(comments),
            unique=len(final_comments),
            duplicates=len(duplicate_map),
            trivial=len(trivial_map)
        )

        return (
            final_comments,
            final_ratings if ratings else [],
            final_indices,
            duplicate_map,
            dedup_info
        )

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Convert to lowercase
        text = text.lower()

        # Remove accents
        text = ''.join(
            c for c in unicodedata.normalize('NFD', text)
            if unicodedata.category(c) != 'Mn'
        )

        # Remove extra whitespace
        text = ' '.join(text.split())

        # Remove punctuation at the end
        text = text.rstrip('.,!?;:')

        return text

    def _quick_similarity(self, text1: str, text2: str) -> float:
        """
        Quick similarity calculation using Jaccard similarity.
        Much faster than Levenshtein distance.
        """
        # Quick length check
        len_diff = abs(len(text1) - len(text2))
        max_len = max(len(text1), len(text2))

        if max_len == 0:
            return 1.0

        if len_diff / max_len > 0.3:  # If lengths differ by more than 30%
            return 0.0

        # Use word-based Jaccard similarity
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union)

    def _is_trivial(self, text: str) -> bool:
        """Check if comment is trivial and should be filtered."""
        # Remove whitespace
        clean = text.strip()

        # Too short
        if len(clean) < 3:
            return True

        # Only punctuation or numbers
        if re.match(r'^[^a-zA-Z]+$', clean):
            return True

        # Common trivial responses
        trivial_phrases = {
            'ok', 'si', 'no', 'yes', 'bien', 'mal',
            'bueno', 'malo', 'gracias', 'thanks',
            'none', 'nada', 'nothing', 'n/a', 'na',
            'sin comentarios', 'no comment'
        }

        if clean.lower() in trivial_phrases:
            return True

        return False