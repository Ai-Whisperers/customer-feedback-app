"""Processing metadata and tracking schemas."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, Any


@dataclass
class ProcessingMetadata:
    """
    Metadata for tracking feedback analysis processing.

    Eliminates data clumps where 4-5 metadata params were passed together.
    Provides centralized calculation of derived metrics.
    """

    task_id: str
    model_used: str
    start_time: datetime = field(default_factory=datetime.now)
    total_comments: int = 0
    valid_comments: int = 0
    batch_count: int = 1
    language_counts: Optional[Dict[str, int]] = None
    dedup_info: Optional[Dict[str, Any]] = None

    @property
    def processing_time_seconds(self) -> float:
        """Calculate elapsed processing time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    @property
    def processing_time_formatted(self) -> str:
        """Get human-readable processing time."""
        seconds = self.processing_time_seconds
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"

    @property
    def invalid_comment_count(self) -> int:
        """Calculate number of invalid comments."""
        return self.total_comments - self.valid_comments

    @property
    def validation_rate(self) -> float:
        """Calculate percentage of valid comments."""
        if self.total_comments == 0:
            return 0.0
        return (self.valid_comments / self.total_comments) * 100

    @property
    def dominant_language(self) -> Optional[str]:
        """Get most common language from language_counts."""
        if not self.language_counts:
            return None
        return max(self.language_counts, key=self.language_counts.get)

    @property
    def deduplication_rate(self) -> float:
        """Calculate percentage of comments that were duplicates."""
        if not self.dedup_info or self.total_comments == 0:
            return 0.0
        duplicates = self.dedup_info.get('duplicates_removed', 0)
        return (duplicates / self.total_comments) * 100

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert metadata to dictionary for storage/serialization.

        Returns:
            Dictionary with all metadata fields and computed properties
        """
        return {
            "task_id": self.task_id,
            "model_used": self.model_used,
            "start_time": self.start_time.isoformat(),
            "processing_time_seconds": round(self.processing_time_seconds, 2),
            "processing_time_formatted": self.processing_time_formatted,
            "total_comments": self.total_comments,
            "valid_comments": self.valid_comments,
            "invalid_comments": self.invalid_comment_count,
            "validation_rate": round(self.validation_rate, 1),
            "batch_count": self.batch_count,
            "language_counts": self.language_counts or {},
            "dominant_language": self.dominant_language,
            "deduplication_info": self.dedup_info or {},
            "deduplication_rate": round(self.deduplication_rate, 1)
        }

    def update_counts(
        self,
        total_comments: Optional[int] = None,
        valid_comments: Optional[int] = None,
        batch_count: Optional[int] = None
    ) -> None:
        """
        Update comment counts.

        Args:
            total_comments: Total number of comments processed
            valid_comments: Number of valid comments
            batch_count: Number of batches created
        """
        if total_comments is not None:
            self.total_comments = total_comments
        if valid_comments is not None:
            self.valid_comments = valid_comments
        if batch_count is not None:
            self.batch_count = batch_count

    def set_language_counts(self, language_counts: Dict[str, int]) -> None:
        """Set language distribution."""
        self.language_counts = language_counts

    def set_dedup_info(self, dedup_info: Dict[str, Any]) -> None:
        """Set deduplication information."""
        self.dedup_info = dedup_info

    def __repr__(self) -> str:
        """String representation for logging."""
        return (
            f"ProcessingMetadata(task_id='{self.task_id}', "
            f"comments={self.total_comments}, "
            f"batches={self.batch_count}, "
            f"time={self.processing_time_formatted})"
        )


@dataclass
class BatchMetadata:
    """
    Metadata for individual batch processing.

    Tracks batch-specific information during parallel processing.
    """

    batch_index: int
    batch_size: int
    language_hint: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.now)

    @property
    def processing_time_seconds(self) -> float:
        """Calculate batch processing time in seconds."""
        return (datetime.now() - self.start_time).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        """Convert batch metadata to dictionary."""
        return {
            "batch_index": self.batch_index,
            "batch_size": self.batch_size,
            "language_hint": self.language_hint,
            "processing_time_seconds": round(self.processing_time_seconds, 2)
        }

    def __repr__(self) -> str:
        """String representation for logging."""
        return (
            f"BatchMetadata(index={self.batch_index}, "
            f"size={self.batch_size}, "
            f"time={self.processing_time_seconds:.1f}s)"
        )
