"""Task status schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .base import TaskStatus


class StatusResponse(BaseModel):
    """Task status response."""
    task_id: str
    status: TaskStatus
    progress: int = Field(ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(
        default=None,
        description="Current processing step"
    )
    estimated_remaining_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="Estimated time remaining"
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="Task start timestamp"
    )
    completed_at: Optional[datetime] = Field(
        default=None,
        description="Task completion timestamp"
    )
    duration_seconds: Optional[float] = Field(
        default=None,
        ge=0,
        description="Total processing time"
    )
    messages: List[str] = Field(
        default_factory=list,
        max_items=10,
        description="Processing messages"
    )
    results_available: bool = Field(
        default=False,
        description="Whether results are ready"
    )
    error: Optional[str] = Field(
        default=None,
        description="Error message if failed"
    )
    details: Optional[str] = Field(
        default=None,
        description="Error details if failed"
    )
    failed_at: Optional[datetime] = Field(
        default=None,
        description="Failure timestamp"
    )
    retry_available: bool = Field(
        default=False,
        description="Whether task can be retried"
    )

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StatusError(BaseModel):
    """Status error response."""
    error: str
    details: str
    code: str = "TASK_NOT_FOUND"