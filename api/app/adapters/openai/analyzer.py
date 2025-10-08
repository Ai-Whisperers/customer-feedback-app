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
from app.utils.openai_logging import (
    OpenAIMetricsCollector,
    ResponseValidator,
    global_metrics
)

logger = structlog.get_logger()


class OpenAIAnalyzer:
    """GPT-4o-mini Chat Completions API client for feedback analysis with structured outputs."""

    def __init__(self):
        """Initialize the OpenAI analyzer."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rate_limiter = create_rate_limiter()
        self.metrics = global_metrics  # Use global metrics collector

    # Removed old verbose methods - now using optimized versions below

    async def _execute_openai_api_call(
        self,
        comments: List[str],
        batch_index: int
    ) -> tuple:
        """
        Execute OpenAI API call and return response with metadata.

        Args:
            comments: List of comments to analyze
            batch_index: Batch index for logging

        Returns:
            Tuple of (response, validated_text)

        Raises:
            openai exceptions for retryable errors
        """
        # Build prompts
        system_prompt = self._build_optimized_system_prompt()
        user_prompt = self._build_optimized_user_prompt(comments)
        response_schema = self._get_response_schema()

        # Execute API call
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
            max_tokens=min(4096, len(comments) * 100),
            seed=42,
            timeout=settings.OPENAI_TIMEOUT_SECONDS
        )

        # Extract and validate response
        result_text = response.choices[0].message.content
        validated_text, is_valid, issues = ResponseValidator.validate_and_repair(
            result_text,
            expected_count=len(comments)
        )

        if issues:
            logger.warning(
                "Response validation issues",
                batch_index=batch_index,
                issues=issues,
                repaired=validated_text != result_text
            )

        return response, validated_text, is_valid

    def _parse_emotion_object(self, obj: Dict[str, Any], index: int) -> Optional[Dict[str, Any]]:
        """
        Parse a single emotion object from API response.

        Args:
            obj: Raw object from API
            index: Object index in array

        Returns:
            Parsed result dict or None if parsing fails
        """
        try:
            # Extract emotions array
            emotions_array = obj.get("e", [])
            if len(emotions_array) < 7:
                logger.warning(f"Incomplete emotions for comment {index}: {emotions_array}")
                return None

            # Build emotions dict from array
            emotions_dict = {
                "satisfaccion": float(emotions_array[0]),
                "frustracion": float(emotions_array[1]),
                "enojo": float(emotions_array[2]),
                "confianza": float(emotions_array[3]),
                "decepcion": float(emotions_array[4]),
                "confusion": float(emotions_array[5]),
                "anticipacion": float(emotions_array[6])
            }

            # Extract churn risk
            churn_risk = float(obj.get("c", 0.5))

            # Extract pain point (optional)
            pain_point = obj.get("p") if obj.get("p") else None

            # Calculate NPS category from emotions
            positive = emotions_dict["satisfaccion"] + emotions_dict["confianza"]
            negative = emotions_dict["frustracion"] + emotions_dict["enojo"] + emotions_dict["decepcion"]

            if positive > 0.7 and negative < 0.3:
                nps_category = "promoter"
            elif negative > 0.5:
                nps_category = "detractor"
            else:
                nps_category = "passive"

            # Build result
            return {
                "index": index,
                "emotions": emotions_dict,
                "churn_risk": churn_risk,
                "pain_points": [pain_point] if pain_point else [],
                "sentiment_score": self._calculate_sentiment_score(emotions_dict),
                "language": "es",
                "nps_category": nps_category,
                "key_phrases": []
            }

        except Exception as e:
            logger.warning(
                "Failed to parse emotion object",
                index=index,
                obj=obj,
                error=str(e)
            )
            return None

    def _create_default_result(self, index: int) -> Dict[str, Any]:
        """
        Create default result for failed parsing.

        Args:
            index: Object index

        Returns:
            Default result dict
        """
        return {
            "index": index,
            "emotions": {k: 0.5 for k in ["satisfaccion", "frustracion", "enojo", "confianza", "decepcion", "confusion", "anticipacion"]},
            "churn_risk": 0.5,
            "pain_points": [],
            "sentiment_score": 0.0,
            "language": "es",
            "nps_category": "passive",
            "key_phrases": []
        }

    def _process_response_objects(
        self,
        objects: List[Dict[str, Any]],
        comments: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Process array of response objects into structured results.

        Args:
            objects: Raw objects from API response
            comments: Original comments (for count validation)

        Returns:
            List of processed result dicts
        """
        # Validate count
        if len(objects) != len(comments):
            logger.warning(
                "Analysis count mismatch",
                expected=len(comments),
                received=len(objects)
            )

        # Process each object
        processed_results = []
        for i, obj in enumerate(objects):
            parsed = self._parse_emotion_object(obj, i)
            if parsed:
                processed_results.append(parsed)
            else:
                # Add default result for failed parsing
                processed_results.append(self._create_default_result(i))

        return processed_results

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
        Analyze a batch of comments using Chat Completions API with structured outputs.

        Orchestrates the analysis pipeline: rate limiting, API call, validation,
        parsing, and error handling.

        Args:
            comments: List of comment strings to analyze
            batch_index: Index of this batch (for logging)
            language_hint: Optional language hint

        Returns:
            Structured analysis results with processed comments

        Raises:
            JSONDecodeError: If response parsing fails
            Exception: For other API errors
        """
        await self.rate_limiter.acquire()
        start_time = time.time()

        # Initialize metrics logging
        prompt_length = sum(len(c) for c in comments)
        context = self.metrics.log_request_start(
            batch_index=batch_index,
            comment_count=len(comments),
            prompt_length=prompt_length
        )

        try:
            # Execute API call and get validated response
            response, validated_text, is_valid = await self._execute_openai_api_call(
                comments, batch_index
            )

            # Log response metrics
            self.metrics.log_response_details(
                context={'batch_index': batch_index, 'comment_count': len(comments), 'timestamp': start_time},
                response=response,
                response_text=validated_text,
                is_complete=is_valid
            )

            # Parse JSON response
            result = json.loads(validated_text)
            objects = result.get("r", [])

            # Process objects into structured results
            processed_results = self._process_response_objects(objects, comments)

            # Log completion metrics
            processing_time = time.time() - start_time
            tokens_used = response.usage.total_tokens if response.usage else 0
            logger.info(
                "Batch analysis completed",
                batch_index=batch_index,
                processing_time=processing_time,
                comments_analyzed=len(processed_results),
                tokens_used=tokens_used,
                tokens_per_comment=round(tokens_used/len(comments), 1) if comments else 0,
                finish_reason=response.choices[0].finish_reason if response.choices else 'unknown'
            )

            return {"comments": processed_results}

        except json.JSONDecodeError as e:
            # Handle JSON parsing errors
            logger.error(
                "Failed to parse OpenAI response",
                batch_index=batch_index,
                error=str(e),
                response_text=validated_text[:500] if 'validated_text' in locals() else None,
                response_length=len(validated_text) if 'validated_text' in locals() else 0
            )

            if hasattr(self, 'metrics'):
                self.metrics.log_error(
                    context={'batch_index': batch_index, 'comment_count': len(comments), 'timestamp': start_time},
                    error=e
                )
            raise

        except Exception as e:
            # Handle all other errors
            processing_time = time.time() - start_time
            error_context = {
                "batch_index": batch_index,
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time": processing_time,
                "comment_count": len(comments)
            }

            if "rate_limit" in str(e).lower():
                error_context["rate_limited"] = True

            logger.error("Batch analysis failed", **error_context)

            if hasattr(self, 'metrics'):
                self.metrics.log_error(
                    context={'batch_index': batch_index, 'comment_count': len(comments), 'timestamp': start_time},
                    error=e
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
        """Build ultra-minimal system prompt."""
        return """Output JSON {"r":[{"e":[7 nums],"c":num,"p":"word?"},...]} per comment.
e: 7 emotions (satisf,frust,anger,trust,disap,confus,antic) 0-1.
c: churn risk 0-1.
p: ONE pain keyword (max 10 chars) if critical, else omit.
Examples: precio,espera,calidad,servicio,app"""

    def _build_optimized_user_prompt(self, comments: List[str]) -> str:
        """Build minimal user prompt."""
        # Ultra-compact format: just number and truncated comment
        formatted = "\n".join([f"{i+1}.{c[:150]}" for i, c in enumerate(comments)])
        return formatted

    def _get_response_schema(self) -> Dict[str, Any]:
        """Get minimal JSON schema for array output."""
        # OpenAI doesn't support oneOf in structured outputs
        # We'll handle mixed types in post-processing
        return {
            "type": "object",
            "properties": {
                "r": {  # 'r' saves tokens vs 'results' or 'analyses'
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "e": {  # emotions array
                                "type": "array",
                                "items": {"type": "number", "minimum": 0, "maximum": 1},
                                "minItems": 7,
                                "maxItems": 7
                            },
                            "c": {  # churn risk
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1
                            },
                            "p": {  # pain point (optional)
                                "type": "string",
                                "maxLength": 10
                            }
                        },
                        "required": ["e", "c", "p"],  # OpenAI requires all properties
                        "additionalProperties": False
                    }
                }
            },
            "required": ["r"],
            "additionalProperties": False
        }