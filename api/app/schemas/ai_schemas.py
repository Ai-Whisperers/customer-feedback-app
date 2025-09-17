"""
Pydantic schemas for OpenAI Responses API with structured outputs.
Defines the exact JSON structure for AI analysis results.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class EmotionScores(BaseModel):
    """Emotion scores from 0 to 1 for each emotion category."""

    # Positive emotions (7)
    alegria: float = Field(ge=0, le=1, description="Joy/Happiness level")
    gratitud: float = Field(ge=0, le=1, description="Gratitude level")
    esperanza: float = Field(ge=0, le=1, description="Hope/Optimism level")
    amor: float = Field(ge=0, le=1, description="Love/Affection level")
    orgullo: float = Field(ge=0, le=1, description="Pride level")
    satisfaccion: float = Field(ge=0, le=1, description="Satisfaction level")
    confianza: float = Field(ge=0, le=1, description="Trust/Confidence level")

    # Negative emotions (7)
    enojo: float = Field(ge=0, le=1, description="Anger level")
    frustracion: float = Field(ge=0, le=1, description="Frustration level")
    miedo: float = Field(ge=0, le=1, description="Fear/Anxiety level")
    tristeza: float = Field(ge=0, le=1, description="Sadness level")
    disgusto: float = Field(ge=0, le=1, description="Disgust level")
    decepcion: float = Field(ge=0, le=1, description="Disappointment level")
    confusion: float = Field(ge=0, le=1, description="Confusion level")

    # Neutral emotions (2)
    sorpresa: float = Field(ge=0, le=1, description="Surprise level")
    anticipacion: float = Field(ge=0, le=1, description="Anticipation level")

    @field_validator('*')
    @classmethod
    def validate_range(cls, v: float) -> float:
        """Ensure all emotion scores are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(f"Emotion score must be between 0 and 1, got {v}")
        return round(v, 3)  # Round to 3 decimal places


class PainPoint(BaseModel):
    """Single pain point extracted from feedback."""

    category: str = Field(
        description="Pain point category (e.g., 'precio', 'calidad', 'servicio', 'entrega')"
    )
    description: str = Field(
        description="Brief description of the specific issue"
    )
    severity: float = Field(
        ge=0, le=1,
        description="Severity level from 0 (minor) to 1 (critical)"
    )


class CommentAnalysis(BaseModel):
    """Complete analysis for a single comment."""

    emotions: EmotionScores = Field(
        description="Emotion scores for all 16 emotions"
    )

    churn_risk: float = Field(
        ge=0, le=1,
        description="Probability of customer churn (0=no risk, 1=certain churn)"
    )

    pain_points: List[PainPoint] = Field(
        default_factory=list,
        max_items=5,
        description="Top pain points identified (max 5)"
    )

    sentiment_score: float = Field(
        ge=-1, le=1,
        description="Overall sentiment (-1=very negative, 0=neutral, 1=very positive)"
    )

    language: str = Field(
        pattern="^(es|en)$",
        description="Detected language: 'es' for Spanish, 'en' for English"
    )

    nps_category: str = Field(
        pattern="^(promoter|passive|detractor)$",
        description="NPS category based on sentiment and content"
    )

    key_phrases: List[str] = Field(
        default_factory=list,
        max_items=3,
        description="Key phrases that summarize the feedback"
    )

    @field_validator('churn_risk', 'sentiment_score')
    @classmethod
    def round_scores(cls, v: float) -> float:
        """Round scores to 3 decimal places."""
        return round(v, 3)


class BatchAnalysisRequest(BaseModel):
    """Request schema for batch analysis."""

    comments: List[str] = Field(
        min_items=1,
        max_items=100,
        description="List of comments to analyze"
    )

    language_hint: Optional[str] = Field(
        default=None,
        pattern="^(es|en)$",
        description="Optional language hint for the batch"
    )

    include_reasoning: bool = Field(
        default=False,
        description="Include reasoning for classifications"
    )


class BatchAnalysisResponse(BaseModel):
    """Response schema for batch analysis."""

    analyses: List[CommentAnalysis] = Field(
        description="Analysis results for each comment"
    )

    batch_metadata: Dict[str, any] = Field(
        default_factory=dict,
        description="Metadata about the batch processing"
    )

    @field_validator('analyses')
    @classmethod
    def validate_count(cls, v: List[CommentAnalysis], info) -> List[CommentAnalysis]:
        """Ensure we have analysis for each comment."""
        if 'comments' in info.context:
            expected_count = len(info.context['comments'])
            if len(v) != expected_count:
                raise ValueError(
                    f"Expected {expected_count} analyses, got {len(v)}"
                )
        return v


class SystemPromptContext(BaseModel):
    """Context for system prompt generation."""

    analysis_language: str = Field(
        default="es",
        pattern="^(es|en)$",
        description="Language for analysis"
    )

    focus_areas: List[str] = Field(
        default_factory=lambda: ["emotions", "churn", "pain_points", "nps"],
        description="Areas to focus analysis on"
    )

    industry_context: Optional[str] = Field(
        default=None,
        description="Optional industry context for better analysis"
    )


class AggregatedMetrics(BaseModel):
    """Aggregated metrics for a complete dataset."""

    total_comments: int = Field(ge=0, description="Total number of comments analyzed")

    average_emotions: EmotionScores = Field(
        description="Average emotion scores across all comments"
    )

    average_churn_risk: float = Field(
        ge=0, le=1,
        description="Average churn risk across all customers"
    )

    top_pain_points: List[Dict[str, any]] = Field(
        description="Top pain points with frequency counts"
    )

    nps_distribution: Dict[str, int] = Field(
        description="Count of promoters, passives, and detractors"
    )

    nps_score: int = Field(
        ge=-100, le=100,
        description="Calculated NPS score"
    )

    language_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of detected languages"
    )

    sentiment_distribution: Dict[str, float] = Field(
        description="Distribution of sentiment scores (positive, neutral, negative percentages)"
    )

    processing_metadata: Dict[str, any] = Field(
        default_factory=dict,
        description="Metadata about processing (time, batches, etc.)"
    )