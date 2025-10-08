"""CSV export strategy."""

import io
from typing import Dict, Any, Tuple

from app.services.export.base_exporter import BaseExporter
from app.services.export.formatters.dataframe_formatter import DataFrameFormatter
from app.schemas.export import ExportInclude


class CSVExporter(BaseExporter):
    """
    CSV export strategy.

    Exports analysis results as CSV file with configurable detail level.
    """

    def __init__(self):
        """Initialize CSV exporter."""
        self.formatter = DataFrameFormatter()

    def export(
        self,
        results: Dict[str, Any],
        include: ExportInclude,
        task_id: str
    ) -> Tuple[bytes, str]:
        """
        Export results to CSV format.

        Args:
            results: Analysis results dictionary
            include: What to include (ALL, SUMMARY, DETAILED)
            task_id: Task identifier

        Returns:
            Tuple of (CSV content as bytes, filename)
        """
        # Validate results structure
        self._validate_results(results)

        # Create DataFrame based on include type
        rows_data = results.get("rows", [])

        if include == ExportInclude.SUMMARY or not rows_data:
            df = self.formatter.create_summary_dataframe(results)
        else:  # ExportInclude.ALL or ExportInclude.DETAILED
            df = self.formatter.create_detailed_dataframe(rows_data)

        # Convert DataFrame to CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding='utf-8')
        csv_content = csv_buffer.getvalue().encode('utf-8')

        # Generate filename
        filename = self._generate_filename(task_id, 'csv')

        return csv_content, filename

    def get_media_type(self) -> str:
        """
        Get MIME type for CSV files.

        Returns:
            CSV MIME type string
        """
        return "text/csv"
