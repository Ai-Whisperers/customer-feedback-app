"""File upload endpoint for feedback analysis."""

import os
import uuid
import base64
from pathlib import Path
import structlog
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional
import pandas as pd
import aiofiles
import redis

from app.config import settings
from app.schemas.upload import UploadResponse, UploadError, FileInfo, UploadOptions
from app.workers.tasks import analyze_feedback

router = APIRouter()
logger = structlog.get_logger()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.xlsx', '.xls', '.csv'}
TEMP_DIR = Path("/tmp/feedback_uploads")
TEMP_DIR.mkdir(exist_ok=True, parents=True)

# Redis client for file storage
redis_client = redis.from_url(settings.REDIS_URL)


@router.post("", response_model=UploadResponse)  # No trailing slash to prevent redirects
async def upload_file(
    file: UploadFile = File(...),
    language_hint: Optional[str] = Form(None),
    segment: Optional[str] = Form(None),
    priority: Optional[str] = Form("normal")
):
    """
    Upload a feedback file for analysis.

    Args:
        file: The uploaded file (Excel or CSV)
        language_hint: Optional language hint (es/en)
        segment: Optional customer segment
        priority: Processing priority (normal/high)

    Returns:
        UploadResponse with task_id and estimated time
    """
    # Validate file extension
    file_extension = Path(file.filename).suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid file format",
                "details": f"File must be one of: {', '.join(ALLOWED_EXTENSIONS)}",
                "code": "INVALID_FILE_FORMAT"
            }
        )

    # Check file size
    file_size = 0
    content = await file.read()
    file_size = len(content)

    if file_size > settings.file_max_bytes:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "File too large",
                "details": f"Maximum file size is {settings.FILE_MAX_MB}MB",
                "code": "FILE_TOO_LARGE"
            }
        )

    # Reset file pointer
    await file.seek(0)

    # Generate unique filename
    task_id = f"t_{uuid.uuid4().hex[:12]}"
    temp_filename = f"{task_id}{file_extension}"
    temp_path = TEMP_DIR / temp_filename

    try:
        # Save file to temporary location
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(content)

        logger.info(
            "File uploaded successfully",
            task_id=task_id,
            filename=file.filename,
            size_mb=round(file_size / 1024 / 1024, 2)
        )

        # Validate file structure
        file_info = await validate_file_structure(temp_path)

        # Create upload options
        options = UploadOptions(
            language_hint=language_hint,
            segment=segment,
            priority=priority
        )

        # Store file content in Redis for worker access
        # Files are stored with 1 hour TTL
        file_key = f"file_content:{task_id}"
        file_data = {
            "content": base64.b64encode(content).decode('utf-8'),
            "filename": file.filename,
            "extension": file_extension
        }
        redis_client.setex(
            file_key,
            3600,  # 1 hour TTL
            str(file_data)
        )

        logger.info(
            "File stored in Redis",
            task_id=task_id,
            key=file_key,
            ttl_seconds=3600
        )

        # Queue analysis task - pass task_id instead of file path
        task = analyze_feedback.apply_async(
            args=[task_id, file_info.dict()],
            task_id=task_id,
            priority=1 if priority == "high" else 0
        )

        # Estimate processing time (roughly 1 second per 100 comments)
        estimated_time = max(10, min(60, file_info.rows // 100))

        return UploadResponse(
            success=True,
            task_id=task_id,
            estimated_time_seconds=estimated_time,
            file_info=file_info
        )

    except pd.errors.EmptyDataError:
        # Clean up temp file and Redis
        if temp_path.exists():
            os.remove(temp_path)
        redis_client.delete(f"file_content:{task_id}")

        raise HTTPException(
            status_code=400,
            detail={
                "error": "Empty file",
                "details": "The uploaded file contains no data",
                "code": "EMPTY_FILE"
            }
        )

    except Exception as e:
        # Clean up temp file and Redis on error
        if temp_path.exists():
            os.remove(temp_path)
        redis_client.delete(f"file_content:{task_id}")

        logger.error(
            "File upload failed",
            error=str(e),
            filename=file.filename,
            exc_info=True
        )

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Upload failed",
                "details": str(e),
                "code": "UPLOAD_ERROR"
            }
        )


async def validate_file_structure(file_path: Path) -> FileInfo:
    """
    Validate the structure of uploaded file.

    Args:
        file_path: Path to the uploaded file

    Returns:
        FileInfo with validation results

    Raises:
        HTTPException if validation fails
    """
    try:
        # Read file based on extension
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path, encoding='utf-8')
        else:
            df = pd.read_excel(file_path)

        # Check for required columns
        required_columns = ['Nota', 'Comentario Final']
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Missing required columns",
                    "details": f"File must contain columns: {', '.join(required_columns)}",
                    "code": "MISSING_COLUMNS",
                    "suggestions": [
                        "Ensure your file has a 'Nota' column with ratings (0-10)",
                        "Ensure your file has a 'Comentario Final' column with feedback text"
                    ]
                }
            )

        # Validate data types and ranges
        valid_rows = 0

        # Check Nota column
        if 'Nota' in df.columns:
            df['Nota'] = pd.to_numeric(df['Nota'], errors='coerce')
            valid_ratings = df['Nota'].between(0, 10, inclusive='both')
            valid_rows = valid_ratings.sum()

        # Check Comentario Final column
        if 'Comentario Final' in df.columns:
            df['Comentario Final'] = df['Comentario Final'].astype(str)
            valid_comments = df['Comentario Final'].str.len() >= 3
            valid_rows = min(valid_rows, valid_comments.sum())

        if valid_rows == 0:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No valid data",
                    "details": "File contains no valid rows after validation",
                    "code": "INVALID_DATA",
                    "suggestions": [
                        "Check that 'Nota' values are between 0 and 10",
                        "Check that 'Comentario Final' has at least 3 characters"
                    ]
                }
            )

        # Check if NPS column exists
        has_nps = 'NPS' in df.columns

        # Get file size in MB
        file_size_mb = round(os.path.getsize(file_path) / 1024 / 1024, 2)

        return FileInfo(
            name=file_path.name,
            rows=valid_rows,
            size_mb=file_size_mb,
            columns_found=list(df.columns),
            has_nps_column=has_nps
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "File validation failed",
            file_path=str(file_path),
            error=str(e),
            exc_info=True
        )
        raise HTTPException(
            status_code=400,
            detail={
                "error": "File validation failed",
                "details": str(e),
                "code": "VALIDATION_ERROR"
            }
        )