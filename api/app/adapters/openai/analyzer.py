"""
OpenAI Chat Completions API analyzer for feedback analysis.
Uses structured outputs with JSON mode for optimal performance.
Implements stable, production-ready Chat Completions with GPT-4o-mini.
"""

import json
import time
import asyncio
from typing import Dict, List, Optional, Any
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai
from openai import AsyncOpenAI

from app.config import settings
from app.schemas.base import Language
from app.schemas.ai_schemas import (
    CommentAnalysis,
    BatchAnalysisResponse,
    EmotionScores,
    PainPoint
)
from app.adapters.openai.client import create_rate_limiter
from app.adapters.openai.utils import optimize_batch_size

logger = structlog.get_logger()


class OpenAIAnalyzer:
    """GPT-4o-mini Chat Completions API client for feedback analysis with structured outputs."""

    def __init__(self):
        """Initialize the OpenAI analyzer."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rate_limiter = create_rate_limiter()

    # Removed old verbose methods - now using optimized versions below

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APIConnectionError,
            openai.APITimeoutError
        ))
    )
    async def analyze_batch(
        self,
        comments: List[str],
        batch_index: int = 0,
        language_hint: Optional[Language] = None
    ) -> Dict[str, Any]:
        """
        Analyze a batch of comments using Responses API with structured outputs.

        Args:
            comments: List of comment strings to analyze
            batch_index: Index of this batch (for logging)
            language_hint: Optional language hint

        Returns:
            Structured analysis results

        Raises:
            JSONDecodeError: If response parsing fails
            Exception: For other API errors
        """
        await self.rate_limiter.acquire()

        start_time = time.time()

        logger.info(
            "Starting batch analysis",
            batch_index=batch_index,
            comment_count=len(comments),
            model=settings.AI_MODEL
        )

        try:
            # Build prompts inline - simpler and clearer
            system_prompt = self._build_optimized_system_prompt()
            user_prompt = self._build_optimized_user_prompt(comments)

            # Define schema inline - no need for external module
            response_schema = self._get_response_schema()

            # Use Chat Completions API with structured output
            response = await self.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "batch_analysis",
                        "schema": response_schema,
                        "strict": True
                    }
                },
                temperature=0.3,
                max_tokens=4096,  # Ensure complete responses
                seed=42  # For reproducibility
            )

            # Extract content from Chat Completions response
            result_text = response.choices[0].message.content

            # Parse the structured output
            result = json.loads(result_text)

            # Validate we got analysis for each comment
            if len(result.get("analyses", [])) != len(comments):
                logger.warning(
                    "Analysis count mismatch",
                    expected=len(comments),
                    received=len(result.get("analyses", []))
                )

            processing_time = time.time() - start_time

            logger.info(
                "Batch analysis completed",
                batch_index=batch_index,
                processing_time=processing_time,
                comments_analyzed=len(result.get("analyses", []))
            )

            # Validate with Pydantic schemas for data integrity
            validated_analyses = []

            for i, analysis in enumerate(result.get("analyses", [])):
                try:
                    # Validate emotions with Pydantic
                    emotions = EmotionScores(**analysis.get("emotions", {}))

                    # Build validated comment analysis
                    comment_data = {
                        "index": i,
                        "emotions": emotions.model_dump(),
                        "churn_risk": analysis.get("churn_risk", 0.5),
                        "pain_points": self._expand_pain_points(analysis.get("pain_points", [])),
                        "sentiment_score": self._calculate_sentiment_score(emotions.model_dump()),
                        "language": "es",  # Default to Spanish
                        "nps_category": analysis.get("nps", "passive"),
                        "key_phrases": []  # Removed to save tokens
                    }

                    validated_analyses.append(comment_data)

                except Exception as e:
                    logger.warning(
                        "Validation failed for comment",
                        index=i,
                        error=str(e)
                    )
                    # Use raw data if validation fails
                    validated_analyses.append({
                        "index": i,
                        "emotions": analysis.get("emotions", {}),
                        "churn_risk": analysis.get("churn_risk", 0.5),
                        "pain_points": self._expand_pain_points(analysis.get("pain_points", [])),
                        "sentiment_score": 0.0,
                        "language": "es",
                        "nps_category": analysis.get("nps", "passive"),
                        "key_phrases": []
                    })

            return {"comments": validated_analyses}

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse OpenAI response",
                batch_index=batch_index,
                error=str(e),
                response_text=result_text[:500] if 'result_text' in locals() else None
            )
            raise

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(
                "Batch analysis failed",
                batch_index=batch_index,
                error=str(e),
                processing_time=processing_time,
                exc_info=True
            )
            raise


    def optimize_batch_size(self, comments: List[str]) -> List[List[str]]:
        """
        Optimize batch sizes for API calls.

        Args:
            comments: List of comments to batch

        Returns:
            List of comment batches
        """
        return optimize_batch_size(comments)


    def _expand_pain_points(self, simple_pain_points: List[str]) -> List[Dict[str, Any]]:
        """
        Convert simple string pain points to structured format.

        Args:
            simple_pain_points: List of simple strings

        Returns:
            List of structured pain point dicts
        """
        return [
            {
                "category": "General",
                "description": pain[:50],  # Truncate if needed
                "severity": 0.7  # Default severity
            }
            for pain in simple_pain_points
        ]

    def _calculate_sentiment_score(self, emotions: Dict[str, float]) -> float:
        """
        Calculate sentiment score from emotions.

        Args:
            emotions: Emotion scores dict

        Returns:
            Sentiment score from -1 to 1
        """
        positive = emotions.get("satisfaccion", 0) + emotions.get("confianza", 0) + emotions.get("anticipacion", 0)
        negative = emotions.get("frustracion", 0) + emotions.get("enojo", 0) + emotions.get("decepcion", 0)
        neutral = emotions.get("confusion", 0)

        # Calculate weighted sentiment
        return round((positive - negative) / max(1, positive + negative + neutral), 2)

    def _build_optimized_system_prompt(self) -> str:
        """Build optimized system prompt with minimal tokens."""
        return """Analyze customer feedback. Extract for each:
EMOTIONS (0-1): satisfaccion, frustracion, enojo, confianza, decepcion, confusion, anticipacion
CHURN_RISK (0-1): probability to leave
PAIN_POINTS: max 2, short strings
NPS: promoter/passive/detractor
Be precise. JSON only."""

    def _build_optimized_user_prompt(self, comments: List[str]) -> str:
        """Build user prompt for batch."""
        formatted = "\n".join([f"{i+1}. {c[:200]}" for i, c in enumerate(comments)])
        return f"Analyze {len(comments)} comments:\n{formatted}\nReturn JSON with 'analyses' array."

    def _get_response_schema(self) -> Dict[str, Any]:
        """Get JSON schema for structured output."""
        return {
            "type": "object",
            "properties": {
                "analyses": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "emotions": {
                                "type": "object",
                                "properties": {
                                    "satisfaccion": {"type": "number", "minimum": 0, "maximum": 1},
                                    "frustracion": {"type": "number", "minimum": 0, "maximum": 1},
                                    "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                    "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                                    "decepcion": {"type": "number", "minimum": 0, "maximum": 1},
                                    "confusion": {"type": "number", "minimum": 0, "maximum": 1},
                                    "anticipacion": {"type": "number", "minimum": 0, "maximum": 1}
                                },
                                "required": ["satisfaccion", "frustracion", "enojo", "confianza", "decepcion", "confusion", "anticipacion"]
                            },
                            "churn_risk": {"type": "number", "minimum": 0, "maximum": 1},
                            "pain_points": {
                                "type": "array",
                                "items": {"type": "string", "maxLength": 30},
                                "maxItems": 2
                            },
                            "nps": {
                                "type": "string",
                                "enum": ["promoter", "passive", "detractor"]
                            }
                        },
                        "required": ["emotions", "churn_risk", "pain_points", "nps"]
                    }
                }
            },
            "required": ["analyses"]
        }