"""
Export service for generating CSV and Excel files.
Handles all export business logic.
"""

import io
from datetime import datetime
from typing import Dict, Any, Tuple
import pandas as pd
import structlog

from app.schemas.export import ExportFormat, ExportInclude

logger = structlog.get_logger()


def generate_export(
    results: Dict[str, Any],
    format: ExportFormat,
    include: ExportInclude,
    task_id: str
) -> Tuple[bytes, str, str]:
    """
    Generate export file from analysis results.

    Args:
        results: Analysis results dictionary
        format: Export format (CSV or XLSX)
        include: What to include in export
        task_id: Task identifier

    Returns:
        Tuple of (file_content, filename, media_type)
    """
    if format == ExportFormat.CSV:
        file_content, filename = _generate_csv_export(results, include, task_id)
        media_type = "text/csv"
    else:  # XLSX
        file_content, filename = _generate_xlsx_export(results, include, task_id)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    logger.info(
        "Export generated",
        task_id=task_id,
        format=format.value,
        include=include.value,
        file_size_kb=len(file_content) / 1024
    )

    return file_content, filename, media_type


def _generate_csv_export(
    results: Dict[str, Any],
    include: ExportInclude,
    task_id: str
) -> Tuple[bytes, str]:
    """Generate CSV export from results."""
    df = _create_dataframe(results, include)

    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_content = csv_buffer.getvalue().encode('utf-8')

    filename = f"analysis_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return csv_content, filename


def _generate_xlsx_export(
    results: Dict[str, Any],
    include: ExportInclude,
    task_id: str
) -> Tuple[bytes, str]:
    """Generate Excel export with multiple sheets."""
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        # Summary sheet
        if include in [ExportInclude.ALL, ExportInclude.SUMMARY]:
            _add_summary_sheet(writer, results)

        # Detailed analysis sheet
        if include in [ExportInclude.ALL, ExportInclude.DETAILED]:
            _add_detailed_sheet(writer, results)

        # Additional sheets for ALL export
        if include == ExportInclude.ALL:
            _add_emotions_sheet(writer, results)
            _add_pain_points_sheet(writer, results)
            _add_metadata_sheet(writer, results)

    excel_buffer.seek(0)
    excel_content = excel_buffer.read()

    filename = f"analysis_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return excel_content, filename


def _create_dataframe(results: Dict[str, Any], include: ExportInclude) -> pd.DataFrame:
    """Create dataframe based on include type."""
    rows_data = results.get("rows", [])

    if include == ExportInclude.SUMMARY or not rows_data:
        return _create_summary_dataframe(results)
    else:
        return _create_detailed_dataframe(rows_data)


def _create_summary_dataframe(results: Dict[str, Any]) -> pd.DataFrame:
    """Create summary dataframe."""
    summary = results.get("summary", {})
    summary_data = {
        "NPS Score": summary.get("nps", {}).get("score"),
        "Total Comments": results.get("metadata", {}).get("total_comments"),
        "Promoters": summary.get("nps", {}).get("promoters"),
        "Passives": summary.get("nps", {}).get("passives"),
        "Detractors": summary.get("nps", {}).get("detractors"),
        "Avg Churn Risk": summary.get("churn_risk", {}).get("average"),
        "High Risk Count": summary.get("churn_risk", {}).get("high_risk_count")
    }
    return pd.DataFrame([summary_data])


def _create_detailed_dataframe(rows_data: list) -> pd.DataFrame:
    """Create detailed dataframe from row data."""
    detailed_data = []

    for row in rows_data:
        row_data = {
            "Index": row.get("index"),
            "Original Text": row.get("original_text"),
            "Rating": row.get("nota"),
            "NPS Category": row.get("nps_category"),
            "Sentiment": row.get("sentiment"),
            "Language": row.get("language"),
            "Churn Risk": row.get("churn_risk"),
            "Pain Points": "; ".join(row.get("pain_points", []))
        }

        # Add emotion columns
        emotions = row.get("emotions", {})
        for emotion, value in emotions.items():
            row_data[f"Emotion_{emotion}"] = value

        detailed_data.append(row_data)

    return pd.DataFrame(detailed_data)


def _add_summary_sheet(writer: pd.ExcelWriter, results: Dict[str, Any]):
    """Add summary sheet to Excel file."""
    summary = results.get("summary", {})
    nps_data = summary.get("nps", {})
    churn_data = summary.get("churn_risk", {})

    summary_df = pd.DataFrame([
        {"Metric": "NPS Score", "Value": nps_data.get("score")},
        {"Metric": "Total Comments", "Value": results.get("metadata", {}).get("total_comments")},
        {"Metric": "Promoters", "Value": f"{nps_data.get('promoters')} ({nps_data.get('promoters_percentage')}%)"},
        {"Metric": "Passives", "Value": f"{nps_data.get('passives')} ({nps_data.get('passives_percentage')}%)"},
        {"Metric": "Detractors", "Value": f"{nps_data.get('detractors')} ({nps_data.get('detractors_percentage')}%)"},
        {"Metric": "Average Churn Risk", "Value": f"{churn_data.get('average', 0):.2%}"},
        {"Metric": "High Risk Customers", "Value": f"{churn_data.get('high_risk_count')} ({churn_data.get('high_risk_percentage')}%)"}
    ])

    summary_df.to_excel(writer, sheet_name='Summary', index=False)


def _add_detailed_sheet(writer: pd.ExcelWriter, results: Dict[str, Any]):
    """Add detailed analysis sheet to Excel file."""
    rows_data = results.get("rows", [])

    if rows_data:
        detailed_data = []
        for row in rows_data:
            row_data = {
                "Index": row.get("index"),
                "Text": row.get("original_text", "")[:100],  # Truncate for Excel
                "Rating": row.get("nota"),
                "NPS": row.get("nps_category"),
                "Sentiment": row.get("sentiment"),
                "Language": row.get("language"),
                "Churn Risk": row.get("churn_risk"),
                "Pain Points": "; ".join(row.get("pain_points", []))
            }
            detailed_data.append(row_data)

        detailed_df = pd.DataFrame(detailed_data)
        detailed_df.to_excel(writer, sheet_name='Detailed', index=False)


def _add_emotions_sheet(writer: pd.ExcelWriter, results: Dict[str, Any]):
    """Add emotions matrix sheet to Excel file."""
    rows_data = results.get("rows", [])

    if rows_data:
        emotions_data = []
        for row in rows_data:
            emotion_row = {"Index": row.get("index")}
            emotions = row.get("emotions", {})
            emotion_row.update(emotions)
            emotions_data.append(emotion_row)

        emotions_df = pd.DataFrame(emotions_data)
        emotions_df.to_excel(writer, sheet_name='Emotions', index=False)


def _add_pain_points_sheet(writer: pd.ExcelWriter, results: Dict[str, Any]):
    """Add pain points sheet to Excel file."""
    pain_points = results.get("summary", {}).get("pain_points", [])

    if pain_points:
        pain_df = pd.DataFrame(pain_points)
        pain_df.to_excel(writer, sheet_name='Pain Points', index=False)


def _add_metadata_sheet(writer: pd.ExcelWriter, results: Dict[str, Any]):
    """Add metadata sheet to Excel file."""
    metadata = results.get("metadata", {})
    meta_df = pd.DataFrame([{
        "Processing Time": f"{metadata.get('processing_time_seconds', 0):.2f} seconds",
        "Model Used": metadata.get("model_used"),
        "Total Comments": metadata.get("total_comments"),
        "Timestamp": metadata.get("timestamp"),
        "Batches Processed": metadata.get("batches_processed")
    }])
    meta_df.to_excel(writer, sheet_name='Metadata', index=False)