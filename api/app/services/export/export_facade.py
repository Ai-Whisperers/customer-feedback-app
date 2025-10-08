"""
Export facade providing unified interface to all export strategies.
Implements Facade pattern to simplify export API.
"""

from typing import Dict, Any, Tuple
import structlog

from app.schemas.export import ExportFormat, ExportInclude
from app.services.export.base_exporter import BaseExporter
from app.services.export.csv_exporter import CSVExporter
from app.services.export.excel_basic_exporter import ExcelBasicExporter
from app.services.export.excel_styled_exporter import ExcelStyledExporter
from app.config import settings

logger = structlog.get_logger()


class ExportFacade:
    """
    Facade for export service.

    Provides simple interface to generate exports in multiple formats.
    Handles strategy selection and coordinates export process.
    """

    def __init__(self):
        """Initialize export facade with all strategies."""
        self._exporters: Dict[str, BaseExporter] = {}
        self._initialize_exporters()

    def _initialize_exporters(self) -> None:
        """Initialize all export strategy instances."""
        # CSV exporter (always available)
        self._exporters['csv'] = CSVExporter()

        # Excel exporters (basic or styled based on config)
        if settings.EXCEL_FORMATTING_ENABLED:
            self._exporters['xlsx'] = ExcelStyledExporter()
            logger.info("Excel exporter initialized with styling enabled")
        else:
            self._exporters['xlsx'] = ExcelBasicExporter()
            logger.info("Excel exporter initialized in basic mode")

    def generate_export(
        self,
        results: Dict[str, Any],
        format: ExportFormat,
        include: ExportInclude,
        task_id: str
    ) -> Tuple[bytes, str, str]:
        """
        Generate export file from analysis results.

        This is the main entry point for export generation.
        Delegates to appropriate strategy based on format.

        Args:
            results: Analysis results dictionary with summary, rows, metadata
            format: Export format (CSV or XLSX)
            include: What to include in export (ALL, SUMMARY, DETAILED)
            task_id: Task identifier for filename generation

        Returns:
            Tuple of (file_content_bytes, filename, media_type)

        Raises:
            ValueError: If format is not supported or results are invalid
            RuntimeError: If export generation fails
        """
        # Validate inputs
        if not results:
            raise ValueError("Results dictionary is empty")

        if not task_id:
            raise ValueError("Task ID is required")

        # Get appropriate exporter
        format_key = format.value.lower()
        exporter = self._exporters.get(format_key)

        if not exporter:
            raise ValueError(f"Unsupported export format: {format.value}")

        # Generate export
        try:
            file_content, filename = exporter.export(results, include, task_id)
            media_type = exporter.get_media_type()

            logger.info(
                "Export generated successfully",
                task_id=task_id,
                format=format.value,
                include=include.value,
                file_size_kb=round(len(file_content) / 1024, 2),
                filename=filename
            )

            return file_content, filename, media_type

        except Exception as e:
            logger.error(
                "Export generation failed",
                task_id=task_id,
                format=format.value,
                error=str(e)
            )
            raise RuntimeError(f"Failed to generate {format.value} export: {str(e)}") from e

    def get_supported_formats(self) -> list[str]:
        """
        Get list of supported export formats.

        Returns:
            List of format names (e.g., ['csv', 'xlsx'])
        """
        return list(self._exporters.keys())

    def is_format_supported(self, format: ExportFormat) -> bool:
        """
        Check if a format is supported.

        Args:
            format: Format to check

        Returns:
            True if format is supported, False otherwise
        """
        return format.value.lower() in self._exporters
