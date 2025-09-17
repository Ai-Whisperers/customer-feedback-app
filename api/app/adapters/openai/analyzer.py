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
            # Build prompts
            system_prompt = self._build_system_prompt(language_hint)
            user_prompt = self._build_user_prompt(comments)

            # Create the structured schema for the response
            response_schema = {
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
                                        "alegria": {"type": "number", "minimum": 0, "maximum": 1},
                                        "gratitud": {"type": "number", "minimum": 0, "maximum": 1},
                                        "esperanza": {"type": "number", "minimum": 0, "maximum": 1},
                                        "amor": {"type": "number", "minimum": 0, "maximum": 1},
                                        "orgullo": {"type": "number", "minimum": 0, "maximum": 1},
                                        "satisfaccion": {"type": "number", "minimum": 0, "maximum": 1},
                                        "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                                        "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                        "frustracion": {"type": "number", "minimum": 0, "maximum": 1},
                                        "miedo": {"type": "number", "minimum": 0, "maximum": 1},
                                        "tristeza": {"type": "number", "minimum": 0, "maximum": 1},
                                        "disgusto": {"type": "number", "minimum": 0, "maximum": 1},
                                        "decepcion": {"type": "number", "minimum": 0, "maximum": 1},
                                        "confusion": {"type": "number", "minimum": 0, "maximum": 1},
                                        "sorpresa": {"type": "number", "minimum": 0, "maximum": 1},
                                        "anticipacion": {"type": "number", "minimum": 0, "maximum": 1}
                                    },
                                    "required": ["alegria", "gratitud", "esperanza", "amor", "orgullo",
                                                "satisfaccion", "confianza", "enojo", "frustracion", "miedo",
                                                "tristeza", "disgusto", "decepcion", "confusion", "sorpresa",
                                                "anticipacion"],
                                    "additionalProperties": False
                                },
                                "churn_risk": {"type": "number", "minimum": 0, "maximum": 1},
                                "pain_points": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "category": {"type": "string"},
                                            "description": {"type": "string"},
                                            "severity": {"type": "number", "minimum": 0, "maximum": 1}
                                        },
                                        "required": ["category", "description", "severity"],
                                        "additionalProperties": False
                                    },
                                    "maxItems": 5
                                },
                                "sentiment_score": {"type": "number", "minimum": -1, "maximum": 1},
                                "language": {"type": "string", "enum": ["es", "en"]},
                                "nps_category": {"type": "string", "enum": ["promoter", "passive", "detractor"]},
                                "key_phrases": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "maxItems": 3
                                }
                            },
                            "required": ["emotions", "churn_risk", "pain_points", "sentiment_score",
                                       "language", "nps_category", "key_phrases"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["analyses"],
                "additionalProperties": False
            }

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
                max_tokens=4000
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
                formatted_result["comments"].append({
                    "index": i,
                    "emotions": analysis["emotions"],
                    "churn_risk": analysis["churn_risk"],
                    "pain_points": analysis["pain_points"],
                    "sentiment_score": analysis["sentiment_score"],
                    "language": analysis["language"],
                    "nps_category": analysis["nps_category"],
                    "key_phrases": analysis.get("key_phrases", [])
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