"""
OpenAI Responses API (GPT-5) analyzer for feedback analysis.
Uses structured outputs exclusively with Responses API for optimal performance.
No Chat Completions fallback - pure Responses API implementation.
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
from app.adapters.openai.optimized_schema import (
    get_optimized_analysis_schema,
    get_optimized_system_prompt,
    get_optimized_user_prompt
)

logger = structlog.get_logger()


class OpenAIAnalyzer:
    """GPT-5 Responses API client for feedback analysis - no fallbacks, pure performance."""

    def __init__(self):
        """Initialize the OpenAI analyzer."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rate_limiter = create_rate_limiter()

    def _build_system_prompt(self, language_hint: Optional[Language] = None) -> str:
        """
        Build the system prompt for analysis.

        Args:
            language_hint: Optional language hint for the batch

        Returns:
            System prompt string
        """
        lang_instruction = ""
        if language_hint:
            lang_map = {"es": "Spanish", "en": "English"}
            lang_instruction = f"The comments are primarily in {lang_map.get(language_hint.value, 'Spanish')}."

        return f"""You are an expert customer feedback analyst specializing in emotional intelligence and business insights.

{lang_instruction}

Analyze each customer comment and provide:

1. EMOTIONS: Score each of the 16 emotions from 0 to 1:
   - Positive: alegria, gratitud, esperanza, amor, orgullo, satisfaccion, confianza
   - Negative: enojo, frustracion, miedo, tristeza, disgusto, decepcion, confusion
   - Neutral: sorpresa, anticipacion

2. CHURN RISK: Estimate probability (0-1) that customer will stop using the service

3. PAIN POINTS: Extract up to 5 main issues with categories and severity

4. NPS CATEGORY: Classify as 'promoter', 'passive', or 'detractor' based on sentiment

5. KEY PHRASES: Extract 1-3 phrases that best summarize the feedback

6. SENTIMENT: Overall sentiment score from -1 (very negative) to 1 (very positive)

7. LANGUAGE: Detect if comment is in 'es' (Spanish) or 'en' (English)

Focus on accuracy and nuance in emotional detection. Be precise with churn risk assessment."""

    def _build_user_prompt(self, comments: List[str]) -> str:
        """
        Build the user prompt with comments.

        Args:
            comments: List of comments to analyze

        Returns:
            User prompt string
        """
        formatted_comments = []
        for i, comment in enumerate(comments, 1):
            # Clean and truncate if needed
            clean_comment = comment.strip()[:1000]
            formatted_comments.append(f"[{i}] {clean_comment}")

        return f"""Analyze these {len(comments)} customer feedback comments:

{chr(10).join(formatted_comments)}

Provide a detailed analysis for EACH comment following the specified JSON structure."""

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
            # Build prompts using optimized versions
            system_prompt = get_optimized_system_prompt()
            user_prompt = get_optimized_user_prompt(comments, batch_index)

            # Get optimized schema (external, modular)
            response_schema = get_optimized_analysis_schema()

            # Use Responses API exclusively (no fallback)
            response = await self.client.responses.create(
                model=settings.AI_MODEL,
                instructions=system_prompt,
                input=user_prompt,
                text={
                    "format": "json_schema",
                    "json_schema": {
                        "name": "batch_analysis",
                        "schema": response_schema,
                        "strict": True
                    }
                },
                temperature=0.3,
                verbosity="low",  # Concise responses for speed
                reasoning_effort="minimal",  # Faster responses without reasoning
                store=False  # Don't store for compliance/ZDR
            )

            # Extract output_text from Responses API
            result_text = response.output_text

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