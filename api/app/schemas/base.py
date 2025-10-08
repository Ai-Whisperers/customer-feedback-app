"""Base schemas and types."""

from enum import Enum
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Task processing status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class NPSCategory(str, Enum):
    """NPS category classification."""
    PROMOTER = "promoter"
    PASSIVE = "passive"
    DETRACTOR = "detractor"


class SentimentCategory(str, Enum):
    """Sentiment classification."""
    VERY_POSITIVE = "muy_positivo"
    POSITIVE = "positivo"
    NEUTRAL = "neutral"
    NEGATIVE = "negativo"
    VERY_NEGATIVE = "muy_negativo"


class Language(str, Enum):
    """Supported languages."""
    SPANISH = "es"
    ENGLISH = "en"


class FileType(str, Enum):
    """Supported file types for upload."""
    CSV = ".csv"
    XLSX = ".xlsx"
    XLS = ".xls"


class EmotionProfile(BaseModel):
    """16 emotions profile with probabilities."""
    # Positive emotions
    alegria: float = Field(ge=0, le=1, description="Joy")
    confianza: float = Field(ge=0, le=1, description="Trust")
    anticipacion: float = Field(ge=0, le=1, description="Anticipation")
    sorpresa_positiva: float = Field(ge=0, le=1, description="Positive surprise")
    amor: float = Field(ge=0, le=1, description="Love")
    optimismo: float = Field(ge=0, le=1, description="Optimism")
    admiracion: float = Field(ge=0, le=1, description="Admiration")

    # Negative emotions
    miedo: float = Field(ge=0, le=1, description="Fear")
    tristeza: float = Field(ge=0, le=1, description="Sadness")
    enojo: float = Field(ge=0, le=1, description="Anger")
    disgusto: float = Field(ge=0, le=1, description="Disgust")
    sorpresa_negativa: float = Field(ge=0, le=1, description="Negative surprise")
    verguenza: float = Field(ge=0, le=1, description="Shame")
    culpa: float = Field(ge=0, le=1, description="Guilt")

    # Neutral emotions
    interes: float = Field(ge=0, le=1, description="Interest")
    confusion: float = Field(ge=0, le=1, description="Confusion")


class NPSMetrics(BaseModel):
    """NPS calculation metrics."""
    score: float = Field(description="NPS score (-100 to 100)")
    promoters: int = Field(ge=0, description="Number of promoters")
    promoters_percentage: float = Field(ge=0, le=100)
    passives: int = Field(ge=0, description="Number of passives")
    passives_percentage: float = Field(ge=0, le=100)
    detractors: int = Field(ge=0, description="Number of detractors")
    detractors_percentage: float = Field(ge=0, le=100)


class ChurnDistribution(BaseModel):
    """Churn risk distribution."""
    very_low: int = Field(ge=0)
    low: int = Field(ge=0)
    moderate: int = Field(ge=0)
    high: int = Field(ge=0)
    very_high: int = Field(ge=0)


class ChurnMetrics(BaseModel):
    """Churn risk metrics."""
    average: float = Field(ge=0, le=1, description="Average churn risk")
    high_risk_count: int = Field(ge=0, description="High risk customers")
    high_risk_percentage: float = Field(ge=0, le=100)
    distribution: ChurnDistribution


class PainPoint(BaseModel):
    """Pain point with frequency and examples."""
    category: str = Field(min_length=1, max_length=100)
    count: int = Field(ge=0)
    percentage: float = Field(ge=0, le=100)
    examples: List[str] = Field(max_items=5, description="Example comments")


class SentimentDistribution(BaseModel):
    """Sentiment distribution counts."""
    muy_positivo: int = Field(ge=0)
    positivo: int = Field(ge=0)
    neutral: int = Field(ge=0)
    negativo: int = Field(ge=0)
    muy_negativo: int = Field(ge=0)


class LanguageDistribution(BaseModel):
    """Language detection distribution."""
    es: int = Field(ge=0, description="Spanish comments")
    en: int = Field(ge=0, description="English comments")


class BaseResponse(BaseModel):
    """Base response model."""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    details: Optional[str] = None
    code: Optional[str] = None