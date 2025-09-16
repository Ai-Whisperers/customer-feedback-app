"""Export results endpoint."""

import json
import io
from datetime import datetime
import pandas as pd
import structlog
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import StreamingResponse

from app.config import settings
from app.schemas.export import ExportFormat, ExportInclude

router = APIRouter()
logger = structlog.get_logger()

# Redis client
import redis
redis_client = redis.from_url(settings.REDIS_URL)


@router.get("/{task_id}")
async def export_results(
    task_id: str = Path(..., description="Task ID from upload endpoint"),
    format: ExportFormat = Query(..., description="Export format (csv or xlsx)"),
    include: ExportInclude = Query(ExportInclude.ALL, description="What to include in export")
):
    """
    Export analysis results in CSV or Excel format.

    Args:
        task_id: The task ID returned from upload endpoint
        format: Export format (csv or xlsx)
        include: What to include (all, summary, or detailed)

    Returns:
        File download response

    Raises:
        404: If results not found
    """
    try:
        # Get results from Redis
        results_key = f"task_results:{task_id}"
        results_data = redis_client.get(results_key)

        if not results_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Results not found",
                    "details": "Task results have expired or do not exist",
                    "code": "RESULTS_NOT_FOUND"
                }
            )

        # Parse results
        results = json.loads(results_data)

        # Generate export based on format
        if format == ExportFormat.CSV:
            file_content, filename = generate_csv_export(results, include, task_id)
            media_type = "text/csv"
        else:  # XLSX
            file_content, filename = generate_xlsx_export(results, include, task_id)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

        logger.info(
            "Export generated",
            task_id=task_id,
            format=format.value,
            include=include.value
        )

        # Return file response
        return StreamingResponse(
            io.BytesIO(file_content),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(
            "Export generation failed",
            task_id=task_id,
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Export failed",
                "details": str(e),
                "code": "EXPORT_ERROR"
            }
        )


def generate_csv_export(results: dict, include: ExportInclude, task_id: str) -> tuple[bytes, str]:
    """
    Generate CSV export from results.

    Args:
        results: Analysis results
        include: What to include
        task_id: Task ID for filename

    Returns:
        Tuple of (file_content, filename)
    """
    rows_data = results.get("rows", [])

    if include == ExportInclude.SUMMARY or not rows_data:
        # Generate summary CSV
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

        df = pd.DataFrame([summary_data])

    elif include == ExportInclude.DETAILED:
        # Generate detailed CSV with row-by-row analysis
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

        df = pd.DataFrame(detailed_data)

    else:  # ALL
        # Generate complete export with both summary and details
        # For CSV, we'll create the detailed version as it's most useful
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

            emotions = row.get("emotions", {})
            for emotion, value in emotions.items():
                row_data[f"Emotion_{emotion}"] = value

            detailed_data.append(row_data)

        df = pd.DataFrame(detailed_data)

    # Convert to CSV
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    csv_content = csv_buffer.getvalue().encode('utf-8')

    filename = f"analysis_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return csv_content, filename


def generate_xlsx_export(results: dict, include: ExportInclude, task_id: str) -> tuple[bytes, str]:
    """
    Generate Excel export from results with multiple sheets.

    Args:
        results: Analysis results
        include: What to include
        task_id: Task ID for filename

    Returns:
        Tuple of (file_content, filename)
    """
    excel_buffer = io.BytesIO()

    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:

        # Sheet 1: Summary
        if include in [ExportInclude.ALL, ExportInclude.SUMMARY]:
            summary = results.get("summary", {})
            nps_data = summary.get("nps", {})
            churn_data = summary.get("churn_risk", {})

            summary_df = pd.DataFrame([{
                "Metric": "NPS Score",
                "Value": nps_data.get("score")
            }, {
                "Metric": "Total Comments",
                "Value": results.get("metadata", {}).get("total_comments")
            }, {
                "Metric": "Promoters",
                "Value": f"{nps_data.get('promoters')} ({nps_data.get('promoters_percentage')}%)"
            }, {
                "Metric": "Passives",
                "Value": f"{nps_data.get('passives')} ({nps_data.get('passives_percentage')}%)"
            }, {
                "Metric": "Detractors",
                "Value": f"{nps_data.get('detractors')} ({nps_data.get('detractors_percentage')}%)"
            }, {
                "Metric": "Average Churn Risk",
                "Value": f"{churn_data.get('average', 0):.2%}"
            }, {
                "Metric": "High Risk Customers",
                "Value": f"{churn_data.get('high_risk_count')} ({churn_data.get('high_risk_percentage')}%)"
            }])

            summary_df.to_excel(writer, sheet_name='Summary', index=False)

        # Sheet 2: Detailed Analysis
        if include in [ExportInclude.ALL, ExportInclude.DETAILED]:
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

        # Sheet 3: Emotions Matrix
        if include == ExportInclude.ALL:
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

        # Sheet 4: Pain Points
        if include == ExportInclude.ALL:
            pain_points = results.get("summary", {}).get("pain_points", [])

            if pain_points:
                pain_df = pd.DataFrame(pain_points)
                pain_df.to_excel(writer, sheet_name='Pain Points', index=False)

        # Sheet 5: Metadata
        if include == ExportInclude.ALL:
            metadata = results.get("metadata", {})
            meta_df = pd.DataFrame([{
                "Processing Time": f"{metadata.get('processing_time_seconds', 0):.2f} seconds",
                "Model Used": metadata.get("model_used"),
                "Total Comments": metadata.get("total_comments"),
                "Timestamp": metadata.get("timestamp"),
                "Batches Processed": metadata.get("batches_processed")
            }])
            meta_df.to_excel(writer, sheet_name='Metadata', index=False)

    excel_buffer.seek(0)
    excel_content = excel_buffer.read()

    filename = f"analysis_{task_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

    return excel_content, filename