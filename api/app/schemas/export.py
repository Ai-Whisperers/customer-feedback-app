"""Export schemas."""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ExportFormat(str, Enum):
    """Export format options."""
    CSV = "csv"
    XLSX = "xlsx"


class ExportInclude(str, Enum):
    """What to include in export."""
    ALL = "all"
    SUMMARY = "summary"
    DETAILED = "detailed"


class ExportRequest(BaseModel):
    """Export request parameters."""
    format: ExportFormat
    include: ExportInclude = Field(default=ExportInclude.ALL)


class ExportError(BaseModel):
    """Export error response."""
    error: str
    details: str
    code: str = "EXPORT_ERROR"