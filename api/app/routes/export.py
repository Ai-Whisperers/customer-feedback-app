"""
Export results endpoint.
Thin controller for export functionality.
"""

import io
import structlog
from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import StreamingResponse

from app.schemas.export import ExportFormat, ExportInclude
from app.services import storage_service, export_service

router = APIRouter()
logger = structlog.get_logger()


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
        500: If export generation fails
    """
    try:
        # Get results from storage
        results = storage_service.get_analysis_results(task_id)

        if not results:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Results not found",
                    "details": "Task results have expired or do not exist",
                    "code": "RESULTS_NOT_FOUND"
                }
            )

        # Generate export
        file_content, filename, media_type = export_service.generate_export(
            results=results,
            format=format,
            include=include,
            task_id=task_id
        )

        logger.info(
            "Export request completed",
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