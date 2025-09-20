"""
OpenAI Responses API analyzer for feedback analysis.
Uses structured outputs with Pydantic schemas for reliable JSON responses.
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
    """OpenAI Responses API client for feedback analysis with structured outputs."""

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

            # Make API call using chat completions (Responses API not yet available in SDK)
            # Using structured outputs with response_format
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
                temperature=0.3,  # Low for consistency
                max_tokens=1500  # Reduced for optimized schema
            )

            # Parse the structured output
            result = json.loads(response.choices[0].message.content)

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

            # Format the result to match expected structure
            formatted_result = {
                "comments": []
            }

            for i, analysis in enumerate(result.get("analyses", [])):
                # Expand simplified schema to full schema for compatibility
                formatted_result["comments"].append({
                    "index": i,
                    "emotions": self._expand_emotions(analysis.get("emotions", {})),
                    "churn_risk": analysis.get("churn_risk", 0.5),
                    "pain_points": self._expand_pain_points(analysis.get("pain_points", [])),
                    "sentiment_score": self._calculate_sentiment_score(analysis.get("emotions", {})),
                    "language": "es",  # Default to Spanish
                    "nps_category": analysis.get("nps", "passive"),
                    "key_phrases": []  # Removed to save tokens
                })

            return formatted_result

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse OpenAI response",
                batch_index=batch_index,
                error=str(e),
                response_text=response.choices[0].message.content[:500] if 'response' in locals() else None
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

    def _expand_emotions(self, simple_emotions: Dict[str, float]) -> Dict[str, float]:
        """
        Expand simplified 5 emotions to full 16 emotions for compatibility.

        Args:
            simple_emotions: Dict with 5 emotions (frustracion, enojo, etc.)

        Returns:
            Dict with 16 emotions matching the original schema
        """
        # Get values from simplified schema
        frustracion = simple_emotions.get("frustracion", 0)
        enojo = simple_emotions.get("enojo", 0)
        satisfaccion = simple_emotions.get("satisfaccion", 0)
        insatisfaccion = simple_emotions.get("insatisfaccion", 0)
        neutral = simple_emotions.get("neutral", 0)

        # Map to 16 emotions
        return {
            # Positive emotions (based on satisfaction)
            "alegria": satisfaccion * 0.8,
            "gratitud": satisfaccion * 0.3,
            "esperanza": max(0, satisfaccion - insatisfaccion) * 0.5,
            "amor": satisfaccion * 0.2,
            "orgullo": satisfaccion * 0.3,
            "satisfaccion": satisfaccion,
            "confianza": satisfaccion * 0.6,
            # Negative emotions (based on frustration/anger)
            "enojo": enojo,
            "frustracion": frustracion,
            "miedo": insatisfaccion * 0.3,
            "tristeza": insatisfaccion * 0.4,
            "disgusto": enojo * 0.6,
            "decepcion": insatisfaccion * 0.7,
            "confusion": neutral * 0.8,
            # Neutral emotions
            "sorpresa": neutral * 0.3,
            "anticipacion": neutral * 0.4
        }

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
        positive = emotions.get("satisfaccion", 0)
        negative = (emotions.get("frustracion", 0) + emotions.get("enojo", 0) +
                   emotions.get("insatisfaccion", 0)) / 3
        return round(positive - negative, 2)