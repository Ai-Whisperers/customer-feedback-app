"""
OpenAI Responses API analyzer for feedback analysis.
"""

import json
import time
from typing import Dict, List, Optional, Any
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import openai

from app.config import settings
from app.schemas.base import Language
from app.adapters.openai.client import create_openai_client, create_rate_limiter
from app.adapters.openai.schemas import get_analysis_schema, build_analysis_instructions
from app.adapters.openai.utils import format_comments_for_analysis, optimize_batch_size

logger = structlog.get_logger()


class OpenAIAnalyzer:
    """OpenAI Responses API client for feedback analysis."""

    def __init__(self):
        """Initialize the OpenAI analyzer."""
        self.client = create_openai_client()
        self.rate_limiter = create_rate_limiter()
        self.analysis_schema = get_analysis_schema()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((
            openai.RateLimitError,
            openai.APIError,
            openai.InternalServerError
        ))
    )
    async def analyze_batch(
        self,
        comments: List[str],
        batch_index: int = 0,
        language_hint: Optional[Language] = None
    ) -> Dict[str, Any]:
        """
        Analyze a batch of comments using Responses API.

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
            # Prepare instructions and input
            instructions = build_analysis_instructions(language_hint)
            input_text = format_comments_for_analysis(comments)

            # Make API call using Responses API
            response = await self.client.responses.create(
                model=settings.AI_MODEL,
                instructions=instructions,
                input=input_text,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "comment_analysis",
                        "schema": self.analysis_schema,
                        "strict": True
                    }
                },
                temperature=0.3,  # Low for consistency
                max_output_tokens=4000
            )

            # Parse the structured output
            result = json.loads(response.output_text)

            processing_time = time.time() - start_time

            logger.info(
                "Batch analysis completed",
                batch_index=batch_index,
                processing_time=processing_time,
                comments_analyzed=len(result.get("comments", []))
            )

            return result

        except json.JSONDecodeError as e:
            logger.error(
                "Failed to parse OpenAI response",
                batch_index=batch_index,
                error=str(e),
                response_text=response.output_text[:500] if 'response' in locals() else None
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