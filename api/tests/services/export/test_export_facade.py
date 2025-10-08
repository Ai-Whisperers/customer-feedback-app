"""Tests for ExportFacade."""

import pytest
from unittest.mock import patch, MagicMock
from app.services.export.export_facade import ExportFacade
from app.schemas.export import ExportFormat, ExportInclude


@pytest.fixture
def sample_results():
    """Sample analysis results for testing."""
    return {
        "task_id": "t_test123456",
        "summary": {
            "nps": {"score": 25.5, "promoters": 30, "passives": 10, "detractors": 20}
        },
        "metadata": {"total_comments": 60, "processing_time_seconds": 12.5},
        "rows": []
    }


class TestExportFacade:
    """Test suite for ExportFacade class."""

    def test_initialization(self):
        """Test facade initializes with all exporters."""
        facade = ExportFacade()
        assert 'csv' in facade._exporters
        assert 'xlsx' in facade._exporters

    def test_csv_export(self, sample_results):
        """Test CSV export through facade."""
        facade = ExportFacade()
        content, filename, media_type = facade.generate_export(
            sample_results,
            ExportFormat.CSV,
            ExportInclude.SUMMARY,
            "t_test123456"
        )

        assert isinstance(content, bytes)
        assert filename.endswith(".csv")
        assert media_type == "text/csv"

    def test_xlsx_export(self, sample_results):
        """Test Excel export through facade."""
        facade = ExportFacade()
        content, filename, media_type = facade.generate_export(
            sample_results,
            ExportFormat.XLSX,
            ExportInclude.SUMMARY,
            "t_test123456"
        )

        assert isinstance(content, bytes)
        assert filename.endswith(".xlsx")
        assert "spreadsheet" in media_type

    def test_get_supported_formats(self):
        """Test getting supported formats."""
        facade = ExportFacade()
        formats = facade.get_supported_formats()

        assert 'csv' in formats
        assert 'xlsx' in formats
        assert isinstance(formats, list)

    def test_is_format_supported(self):
        """Test format support check."""
        facade = ExportFacade()

        assert facade.is_format_supported(ExportFormat.CSV) is True
        assert facade.is_format_supported(ExportFormat.XLSX) is True

    def test_empty_results_raises_error(self):
        """Test that empty results raise ValueError."""
        facade = ExportFacade()

        with pytest.raises(ValueError, match="Results dictionary is empty"):
            facade.generate_export(
                {},
                ExportFormat.CSV,
                ExportInclude.ALL,
                "t_test123456"
            )

    def test_empty_task_id_raises_error(self, sample_results):
        """Test that empty task_id raises ValueError."""
        facade = ExportFacade()

        with pytest.raises(ValueError, match="Task ID is required"):
            facade.generate_export(
                sample_results,
                ExportFormat.CSV,
                ExportInclude.ALL,
                ""
            )

    def test_export_error_handling(self, sample_results):
        """Test that export errors are properly wrapped."""
        facade = ExportFacade()

        # Mock exporter to raise an exception
        with patch.object(facade._exporters['csv'], 'export', side_effect=Exception("Test error")):
            with pytest.raises(RuntimeError, match="Failed to generate csv export"):
                facade.generate_export(
                    sample_results,
                    ExportFormat.CSV,
                    ExportInclude.ALL,
                    "t_test123456"
                )

    @patch('app.services.export.export_facade.settings')
    def test_excel_formatter_selection(self, mock_settings):
        """Test that Excel formatter is selected based on settings."""
        # Test styled exporter when formatting is enabled
        mock_settings.EXCEL_FORMATTING_ENABLED = True
        facade = ExportFacade()

        assert 'xlsx' in facade._exporters
        # The exporter should be StyledExporter (can check via class name)
        from app.services.export.excel_styled_exporter import ExcelStyledExporter
        assert isinstance(facade._exporters['xlsx'], ExcelStyledExporter)

    def test_different_include_options(self, sample_results):
        """Test facade works with different include options."""
        facade = ExportFacade()

        # Test SUMMARY
        content_summary, _, _ = facade.generate_export(
            sample_results, ExportFormat.CSV, ExportInclude.SUMMARY, "t_test"
        )
        assert isinstance(content_summary, bytes)

        # Test DETAILED (will fallback to summary since no rows)
        content_detailed, _, _ = facade.generate_export(
            sample_results, ExportFormat.CSV, ExportInclude.DETAILED, "t_test"
        )
        assert isinstance(content_detailed, bytes)

        # Test ALL
        content_all, _, _ = facade.generate_export(
            sample_results, ExportFormat.CSV, ExportInclude.ALL, "t_test"
        )
        assert isinstance(content_all, bytes)
