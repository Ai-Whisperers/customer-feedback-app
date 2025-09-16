"""Upload related schemas."""

from typing import Optional
from pydantic import BaseModel, Field

from .base import BaseResponse, Language


class UploadOptions(BaseModel):
    """Optional upload parameters."""
    language_hint: Optional[Language] = Field(
        default=None,
        description="Language hint for processing"
    )
    segment: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Customer segment identifier"
    )
    priority: Optional[str] = Field(
        default="normal",
        regex="^(normal|high)$",
        description="Processing priority"
    )


class FileInfo(BaseModel):
    """File information."""
    name: str = Field(max_length=255, description="Original filename")
    rows: int = Field(ge=0, description="Number of valid rows")
    size_mb: float = Field(ge=0, description="File size in MB")
    columns_found: list[str] = Field(description="Detected columns")
    has_nps_column: bool = Field(description="Whether NPS column exists")


class UploadResponse(BaseResponse):
    """Upload endpoint response."""
    task_id: str = Field(description="Unique task identifier")
    estimated_time_seconds: int = Field(ge=0, description="Estimated processing time")
    file_info: FileInfo


class UploadError(BaseModel):
    """Upload error response."""
    error: str
    details: str
    code: str
    suggestions: Optional[list[str]] = Field(
        default=None,
        description="Suggestions to fix the error"
    )