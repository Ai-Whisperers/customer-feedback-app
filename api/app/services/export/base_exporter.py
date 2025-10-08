"""Base exporter interface for all export strategies."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple
from datetime import datetime

from app.schemas.export import ExportInclude


class BaseExporter(ABC):
    """
    Abstract base class for export strategies.

    Implements Strategy pattern for different export formats.
    Each concrete exporter handles one specific format (CSV, Excel basic, Excel styled).
    """

    @abstractmethod
    def export(
        self,
        results: Dict[str, Any],
        include: ExportInclude,
        task_id: str
    ) -> Tuple[bytes, str]:
        """
        Export results to file format.

        Args:
            results: Analysis results dictionary with summary, rows, metadata
            include: What to include in export (ALL, SUMMARY, DETAILED)
            task_id: Task identifier for filename generation

        Returns:
            Tuple of (file_content_bytes, filename)

        Raises:
            ValueError: If export parameters are invalid
            RuntimeError: If export generation fails
        """
        pass

    @abstractmethod
    def get_media_type(self) -> str:
        """
        Get MIME type for this export format.

        Returns:
            MIME type string (e.g., 'text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        """
        pass

    def _generate_filename(self, task_id: str, extension: str) -> str:
        """
        Generate timestamped filename for export.

        Args:
            task_id: Task identifier
            extension: File extension without dot (e.g., 'csv', 'xlsx')

        Returns:
            Filename string like 'analysis_t_abc123_20251008_143022.csv'
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"analysis_{task_id}_{timestamp}.{extension}"

    def _validate_results(self, results: Dict[str, Any]) -> None:
        """
        Validate that results dictionary has required fields.

        Args:
            results: Results dictionary to validate

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ['summary', 'metadata']

        for field in required_fields:
            if field not in results:
                raise ValueError(f"Results missing required field: {field}")

        # Validate summary structure
        if 'nps' not in results['summary']:
            raise ValueError("Results summary missing NPS data")
