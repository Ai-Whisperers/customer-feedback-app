"""Analysis result schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .base import (
    EmotionProfile,
    NPSMetrics,
    ChurnMetrics,
    PainPoint,
    SentimentDistribution,
    LanguageDistribution,
    NPSCategory,
    SentimentCategory,
    Language
)


class CommentAnalysis(BaseModel):
    """Individual comment analysis result."""
    index: int = Field(ge=0, description="Original row index")
    original_text: str = Field(max_length=2000, description="Original comment text")
    nota: int = Field(ge=0, le=10, description="Original rating")
    nps_category: NPSCategory
    emotions: EmotionProfile
    churn_risk: float = Field(ge=0, le=1, description="Churn probability")
    pain_points: List[str] = Field(max_items=5, description="Extracted pain points")
    sentiment: SentimentCategory
    language: Language


class SegmentProfile(BaseModel):
    """Profile analysis for a segment."""
    dominant_emotions: List[str] = Field(max_items=5)
    common_mentions: List[str] = Field(max_items=10)
    avg_churn_risk: float = Field(ge=0, le=1)
    sentiment_score: float = Field(ge=-1, le=1)


class AggregatedInsights(BaseModel):
    """Aggregated insights and recommendations."""
    top_positive_themes: List[str] = Field(max_items=10)
    top_negative_themes: List[str] = Field(max_items=10)
    recommendations: List[str] = Field(max_items=5)
    segment_analysis: dict[str, SegmentProfile] = Field(
        default_factory=dict,
        description="Analysis by NPS segment"
    )


class ProcessingMetadata(BaseModel):
    """Processing metadata."""
    total_comments: int = Field(ge=0)
    processing_time_seconds: float = Field(ge=0)
    model_used: str
    timestamp: datetime
    language_distribution: LanguageDistribution
    batches_processed: int = Field(ge=0)
    tokens_used: Optional[int] = Field(default=None, ge=0)


class AnalysisSummary(BaseModel):
    """Summary of analysis results."""
    nps: NPSMetrics
    emotions: EmotionProfile  # Average emotions across all comments
    churn_risk: ChurnMetrics
    pain_points: List[PainPoint] = Field(max_items=20)
    sentiment_distribution: SentimentDistribution


class AnalysisResults(BaseModel):
    """Complete analysis results."""
    task_id: str
    metadata: ProcessingMetadata
    summary: AnalysisSummary
    rows: List[CommentAnalysis] = Field(description="Per-comment analysis")
    aggregated_insights: AggregatedInsights

    class Config:
        """Pydantic config."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }