"""Tests for CSV exporter."""

import pytest
from app.services.export.csv_exporter import CSVExporter
from app.schemas.export import ExportInclude


@pytest.fixture
def sample_results():
    """Sample analysis results for testing."""
    return {
        "task_id": "t_test123456",
        "summary": {
            "nps": {
                "score": 25.5,
                "promoters": 30,
                "promoters_percentage": 50.0,
                "passives": 10,
                "passives_percentage": 16.7,
                "detractors": 20,
                "detractors_percentage": 33.3
            },
            "churn_risk": {
                "average": 0.35,
                "high_risk_count": 15,
                "high_risk_percentage": 25.0
            },
            "pain_points": [
                {"category": "Slow support", "count": 25, "percentage": 41.7},
                {"category": "High price", "count": 15, "percentage": 25.0}
            ]
        },
        "metadata": {
            "total_comments": 60,
            "processing_time_seconds": 12.5,
            "model_used": "gpt-4o-mini",
            "batches_processed": 2
        },
        "rows": [
            {
                "index": 0,
                "original_text": "Great service!",
                "nota": 9,
                "nps_category": "promoter",
                "sentiment": "positive",
                "language": "en",
                "churn_risk": 0.1,
                "pain_points": [],
                "emotions": {"satisfaccion": 0.9, "alegria": 0.7}
            },
            {
                "index": 1,
                "original_text": "Too slow",
                "nota": 3,
                "nps_category": "detractor",
                "sentiment": "negative",
                "language": "en",
                "churn_risk": 0.8,
                "pain_points": ["slow support"],
                "emotions": {"frustracion": 0.8, "enojo": 0.6}
            }
        ]
    }


class TestCSVExporter:
    """Test suite for CSVExporter class."""

    def test_initialization(self):
        """Test CSVExporter initializes correctly."""
        exporter = CSVExporter()
        assert exporter.formatter is not None

    def test_get_media_type(self):
        """Test get_media_type returns correct MIME type."""
        exporter = CSVExporter()
        assert exporter.get_media_type() == "text/csv"

    def test_export_summary(self, sample_results):
        """Test exporting summary data."""
        exporter = CSVExporter()
        content, filename = exporter.export(
            sample_results,
            ExportInclude.SUMMARY,
            "t_test123456"
        )

        # Verify content is bytes
        assert isinstance(content, bytes)

        # Verify content contains summary metrics
        content_str = content.decode('utf-8')
        assert "NPS Score" in content_str
        assert "25.5" in content_str
        assert "Total Comentarios" in content_str

        # Verify filename format
        assert filename.startswith("analysis_t_test123456_")
        assert filename.endswith(".csv")

    def test_export_detailed(self, sample_results):
        """Test exporting detailed data."""
        exporter = CSVExporter()
        content, filename = exporter.export(
            sample_results,
            ExportInclude.DETAILED,
            "t_test123456"
        )

        # Verify content is bytes
        assert isinstance(content, bytes)

        # Verify content contains row data
        content_str = content.decode('utf-8')
        assert "Great service!" in content_str
        assert "Too slow" in content_str
        assert "promoter" in content_str
        assert "detractor" in content_str

    def test_export_all(self, sample_results):
        """Test exporting all data defaults to detailed view."""
        exporter = CSVExporter()
        content, filename = exporter.export(
            sample_results,
            ExportInclude.ALL,
            "t_test123456"
        )

        # For CSV, ALL should return detailed view
        content_str = content.decode('utf-8')
        assert "Great service!" in content_str
        assert "Index" in content_str

    def test_export_empty_rows(self, sample_results):
        """Test exporting when no rows are present."""
        sample_results["rows"] = []
        exporter = CSVExporter()

        content, filename = exporter.export(
            sample_results,
            ExportInclude.ALL,
            "t_test123456"
        )

        # Should fallback to summary
        content_str = content.decode('utf-8')
        assert "NPS Score" in content_str

    def test_export_validates_results(self):
        """Test that export validates results structure."""
        exporter = CSVExporter()

        with pytest.raises(ValueError, match="Results missing required field"):
            exporter.export(
                {"invalid": "data"},
                ExportInclude.ALL,
                "t_test123456"
            )

    def test_filename_generation(self, sample_results):
        """Test filename includes task_id and timestamp."""
        exporter = CSVExporter()
        _, filename1 = exporter.export(sample_results, ExportInclude.SUMMARY, "t_abc")
        _, filename2 = exporter.export(sample_results, ExportInclude.SUMMARY, "t_xyz")

        # Different task IDs should generate different filenames
        assert "t_abc" in filename1
        assert "t_xyz" in filename2
        assert filename1 != filename2
