"""
Async OpenAI analyzer for parallel processing.
Handles concurrent API calls with rate limiting.
"""

import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
import structlog
from datetime import datetime

from app.config import settings

logger = structlog.get_logger()


class AsyncOpenAIAnalyzer:
    """Async analyzer for parallel OpenAI API calls."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_concurrent: Optional[int] = None,
        rate_limit_rps: Optional[int] = None
    ):
        """
        Initialize async analyzer.

        Args:
            api_key: OpenAI API key
            model: Model to use
            max_concurrent: Maximum concurrent requests
            rate_limit_rps: Rate limit in requests per second
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.AI_MODEL
        self.max_concurrent = max_concurrent or settings.OPENAI_CONCURRENT_WORKERS
        self.rate_limit_rps = rate_limit_rps or settings.MAX_RPS

        # Semaphore for concurrency control
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        # Track request timing for rate limiting
        self.request_times = []
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Context manager entry."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.session:
            await self.session.close()

    async def _rate_limit(self):
        """Implement rate limiting."""
        now = asyncio.get_event_loop().time()

        # Clean old request times
        cutoff = now - 1.0  # 1 second window
        self.request_times = [t for t in self.request_times if t > cutoff]

        # If at rate limit, wait
        if len(self.request_times) >= self.rate_limit_rps:
            wait_time = 1.0 - (now - self.request_times[0])
            if wait_time > 0:
                await asyncio.sleep(wait_time)

        # Record this request
        self.request_times.append(now)

    def _build_request(
        self,
        comments: List[str],
        language_hint: str = "es"
    ) -> Dict[str, Any]:
        """
        Build OpenAI API request.

        Args:
            comments: List of comments to analyze
            language_hint: Language hint for analysis

        Returns:
            Request payload
        """
        # Build prompt for batch analysis
        comments_text = "\n".join([
            f"[{i}]: {comment}"
            for i, comment in enumerate(comments)
        ])

        system_prompt = f"""You are an expert sentiment and emotion analyzer.
Analyze customer feedback in {language_hint} language.
For each comment, extract:
1. 16 emotions (probability 0-1): joy, trust, fear, surprise, sadness, disgust, anger, anticipation, love, optimism, pessimism, hope, anxiety, envy, guilt, pride
2. Churn risk score (0-1)
3. Pain points mentioned
4. NPS category if not provided"""

        user_prompt = f"""Analyze these {len(comments)} comments and return JSON array:
{comments_text}

Return format:
[{{"index": 0, "emotions": {{...}}, "churn_risk": 0.x, "pain_points": [...], "nps": "..."}}]"""

        return {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.3,
            "max_tokens": min(4096, len(comments) * 150)
        }

    async def analyze_batch(
        self,
        comments: List[str],
        language_hint: str = "es",
        retry_count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Analyze a batch of comments asynchronously.

        Args:
            comments: List of comments
            language_hint: Language hint
            retry_count: Number of retries on failure

        Returns:
            List of analysis results
        """
        async with self.semaphore:
            await self._rate_limit()

            for attempt in range(retry_count):
                try:
                    start_time = datetime.now()

                    async with self.session.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json"
                        },
                        json=self._build_request(comments, language_hint),
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        if response.status == 429:  # Rate limited
                            wait_time = 2 ** attempt
                            logger.warning(
                                "Rate limited, retrying",
                                attempt=attempt,
                                wait_seconds=wait_time
                            )
                            await asyncio.sleep(wait_time)
                            continue

                        response.raise_for_status()
                        result = await response.json()

                        # Log performance
                        elapsed = (datetime.now() - start_time).total_seconds()
                        if settings.LOG_PERFORMANCE_METRICS:
                            logger.info(
                                "Batch analyzed",
                                batch_size=len(comments),
                                elapsed_seconds=elapsed,
                                tokens_used=result.get("usage", {}).get("total_tokens", 0)
                            )

                        # Parse response
                        return self._parse_response(result, len(comments))

                except asyncio.TimeoutError:
                    logger.error(
                        "Request timeout",
                        attempt=attempt,
                        batch_size=len(comments)
                    )
                    if attempt == retry_count - 1:
                        raise

                except Exception as e:
                    logger.error(
                        "Batch analysis failed",
                        attempt=attempt,
                        error=str(e)
                    )
                    if attempt == retry_count - 1:
                        raise

                await asyncio.sleep(2 ** attempt)

        return []

    def _parse_response(
        self,
        response: Dict[str, Any],
        expected_count: int
    ) -> List[Dict[str, Any]]:
        """
        Parse OpenAI response.

        Args:
            response: API response
            expected_count: Expected number of results

        Returns:
            Parsed results
        """
        try:
            content = response["choices"][0]["message"]["content"]
            results = json.loads(content)

            # Ensure we have all results
            if len(results) < expected_count:
                logger.warning(
                    "Incomplete results",
                    expected=expected_count,
                    received=len(results)
                )
                # Pad with default values
                for i in range(len(results), expected_count):
                    results.append(self._get_default_result(i))

            return results

        except (KeyError, json.JSONDecodeError) as e:
            logger.error("Failed to parse response", error=str(e))
            return [
                self._get_default_result(i)
                for i in range(expected_count)
            ]

    def _get_default_result(self, index: int) -> Dict[str, Any]:
        """Get default result for failed analysis."""
        return {
            "index": index,
            "emotions": {
                emotion: 0.0
                for emotion in [
                    "joy", "trust", "fear", "surprise",
                    "sadness", "disgust", "anger", "anticipation",
                    "love", "optimism", "pessimism", "hope",
                    "anxiety", "envy", "guilt", "pride"
                ]
            },
            "churn_risk": 0.5,
            "pain_points": [],
            "nps": "passive"
        }

    async def analyze_all_batches(
        self,
        batches: List[List[str]],
        language_hint: str = "es",
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Analyze multiple batches in parallel.

        Args:
            batches: List of comment batches
            language_hint: Language hint
            progress_callback: Optional callback for progress updates

        Returns:
            All results combined
        """
        logger.info(
            "Starting parallel batch analysis",
            total_batches=len(batches),
            concurrent_workers=self.max_concurrent
        )

        # Create tasks for all batches
        tasks = []
        for i, batch in enumerate(batches):
            task = self.analyze_batch(batch, language_hint)
            tasks.append(task)

        # Execute with progress tracking
        all_results = []
        completed = 0

        for task in asyncio.as_completed(tasks):
            results = await task
            all_results.extend(results)
            completed += 1

            if progress_callback:
                progress = int((completed / len(batches)) * 100)
                await progress_callback(progress)

            logger.info(
                "Batch completed",
                completed=completed,
                total=len(batches),
                progress_percent=int((completed / len(batches)) * 100)
            )

        return all_results


async def create_analyzer() -> AsyncOpenAIAnalyzer:
    """Factory function to create analyzer instance."""
    analyzer = AsyncOpenAIAnalyzer()
    await analyzer.__aenter__()
    return analyzer