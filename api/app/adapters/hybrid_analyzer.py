"""
Hybrid analyzer orchestrating local sentiment + OpenAI insights.
Memory-aware for 512MB constraint.
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
import structlog
import psutil
from concurrent.futures import ThreadPoolExecutor

from app.adapters.local_sentiment import LocalSentimentAnalyzer
from app.adapters.openai.analyzer import OpenAIAnalyzer
from app.config import settings

logger = structlog.get_logger()


class HybridAnalyzer:
    """
    Orchestrates local sentiment + OpenAI insights.
    Memory-aware for 512MB constraint.
    """

    def __init__(self):
        self.local_analyzer = LocalSentimentAnalyzer()
        self.openai_analyzer = OpenAIAnalyzer()
        self.executor = ThreadPoolExecutor(max_workers=2)

    def analyze_batch(
        self,
        comments: List[str],
        batch_index: int = 0,
        language_hint: str = "es"
    ) -> Dict:
        """
        Hybrid analysis: local emotions + AI insights.

        Process:
        1. Local sentiment analysis (fast, free)
        2. Prepare minimal context for OpenAI
        3. Get insights (churn risk, pain points) from OpenAI
        4. Merge results
        """

        # Check memory before processing
        memory_mb = psutil.virtual_memory().available / (1024 * 1024)
        if memory_mb < 100:
            logger.warning(f"Low memory: {memory_mb:.1f}MB available")
            # Reduce batch size if memory is low
            if len(comments) > 20:
                comments = comments[:20]

        try:
            # Step 1: Local sentiment (run in thread to avoid blocking)
            local_future = self.executor.submit(
                self.local_analyzer.analyze_batch,
                comments,
                language_hint
            )

            # Step 2: Prepare optimized prompts for OpenAI
            # Include sentiment context to improve accuracy
            # Get local results from the future
            local_results = local_future.result(timeout=5)

            enriched_prompts = self._prepare_insight_prompts(
                comments, local_results
            )

            # Step 3: Get insights from OpenAI (only what we need)
            # Run async operation in sync context
            loop = asyncio.new_event_loop()
            try:
                insights = loop.run_until_complete(
                    self._get_ai_insights(enriched_prompts, batch_index)
                )
            finally:
                loop.close()

            # Step 4: Merge results
            final_results = self._merge_results(
                comments, local_results, insights
            )

            logger.info(
                "Hybrid analysis completed",
                batch_index=batch_index,
                comments=len(comments),
                memory_used_mb=round((psutil.virtual_memory().percent), 1)
            )

            return {"comments": final_results}

        except Exception as e:
            logger.error(f"Hybrid analysis failed: {str(e)}", exc_info=True)
            # Fallback to local only
            return self._fallback_local_only(comments, local_results if 'local_results' in locals() else None)

    def _prepare_insight_prompts(
        self,
        comments: List[str],
        local_results: List[Dict]
    ) -> List[Tuple[str, Dict]]:
        """
        Prepare enriched prompts with sentiment context.
        This helps OpenAI focus on insights rather than basic sentiment.
        """
        enriched = []

        for comment, local in zip(comments, local_results):
            sentiment = local['base_sentiment']

            # Create context string
            context = f"[Sentiment: {'positive' if sentiment['compound'] > 0.1 else 'negative' if sentiment['compound'] < -0.1 else 'neutral'}]"

            # Truncate comment but keep sentiment context
            enriched_comment = f"{context} {comment[:120]}"
            enriched.append((enriched_comment, sentiment))

        return enriched

    async def _get_ai_insights(
        self,
        enriched_prompts: List[Tuple[str, Dict]],
        batch_index: int
    ) -> List[Dict]:
        """
        Get ONLY insights from OpenAI (not emotions).
        Uses optimized prompt focusing on churn risk and pain points.
        """

        # Build optimized prompt for insights only
        system_prompt = """Extract ONLY: churn risk (0-1) and pain category.
Comments include [Sentiment: positive/negative/neutral] context.
Output: {"r":[{"c":0.0-1.0,"p":"category"},...]}
Categories: precio,calidad,servicio,tiempo,app,producto,atencion,otro"""

        # Format comments with context
        formatted_comments = [enriched[0] for enriched in enriched_prompts]
        user_prompt = "\n".join([f"{i+1}.{c}" for i, c in enumerate(formatted_comments)])

        # Simpler schema without emotions
        response_schema = {
            "type": "object",
            "properties": {
                "r": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "c": {"type": "number", "minimum": 0, "maximum": 1},  # churn risk
                            "p": {"type": "string", "maxLength": 15}  # pain category
                        },
                        "required": ["c", "p"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["r"],
            "additionalProperties": False
        }

        # Make the API call with reduced token usage
        try:
            # Rate limiting
            await self.openai_analyzer.rate_limiter.acquire()

            response = await self.openai_analyzer.client.chat.completions.create(
                model=settings.AI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "insights",
                        "schema": response_schema,
                        "strict": True
                    }
                },
                temperature=0.3,
                max_tokens=len(formatted_comments) * 30,  # Much less needed without emotions
                seed=42,
                timeout=30  # Explicit timeout
            )

            result = json.loads(response.choices[0].message.content)
            insights = result.get("r", [])

            # Log token usage
            if response.usage:
                logger.info(
                    "OpenAI insights extracted",
                    batch_index=batch_index,
                    tokens_used=response.usage.total_tokens,
                    tokens_per_comment=round(response.usage.total_tokens/len(formatted_comments), 1)
                )

            # Ensure we have insights for each comment
            while len(insights) < len(formatted_comments):
                insights.append({"c": 0.5, "p": "otro"})

            return insights

        except Exception as e:
            logger.error(f"OpenAI insights failed: {e}")
            # Return default insights
            return [{"c": 0.5, "p": "otro"} for _ in formatted_comments]

    def _merge_results(
        self,
        comments: List[str],
        local_results: List[Dict],
        insights: List[Dict]
    ) -> List[Dict]:
        """
        Merge local emotions with AI insights.
        Maintains exact frontend contract.
        """
        merged = []

        for i, (comment, local, insight) in enumerate(zip(comments, local_results, insights)):
            # Calculate NPS from emotions (maintain compatibility)
            emotions = local['emotions']
            positive = emotions["satisfaccion"] + emotions["confianza"]
            negative = emotions["frustracion"] + emotions["enojo"] + emotions["decepcion"]

            if positive > 0.7 and negative < 0.3:
                nps_category = "promoter"
            elif negative > 0.5:
                nps_category = "detractor"
            else:
                nps_category = "passive"

            merged.append({
                "index": i,
                "emotions": emotions,  # From local analysis
                "churn_risk": insight.get("c", 0.5),  # From OpenAI
                "pain_points": [insight.get("p")] if insight.get("p") and insight.get("p") != "otro" else [],
                "sentiment_score": local['base_sentiment']['compound'],
                "language": "es",
                "nps_category": nps_category,
                "key_phrases": []
            })

        return merged

    def _fallback_local_only(self, comments: List[str], local_results: Optional[List[Dict]]) -> Dict:
        """
        Fallback when OpenAI fails.
        Uses only local analysis with default churn risk.
        """
        if not local_results:
            local_results = self.local_analyzer.analyze_batch(comments)

        results = []
        for i, (comment, local) in enumerate(zip(comments, local_results)):
            emotions = local['emotions']

            # Estimate churn risk from emotions
            negative_score = emotions["frustracion"] + emotions["enojo"] + emotions["decepcion"]
            churn_risk = min(1.0, negative_score / 1.5)

            # Basic pain point detection from keywords
            pain_point = self._detect_basic_pain_point(comment)

            # NPS from emotions
            positive = emotions["satisfaccion"] + emotions["confianza"]
            negative = emotions["frustracion"] + emotions["enojo"] + emotions["decepcion"]

            if positive > 0.7 and negative < 0.3:
                nps_category = "promoter"
            elif negative > 0.5:
                nps_category = "detractor"
            else:
                nps_category = "passive"

            results.append({
                "index": i,
                "emotions": emotions,
                "churn_risk": churn_risk,
                "pain_points": [pain_point] if pain_point else [],
                "sentiment_score": local['base_sentiment']['compound'],
                "language": "es",
                "nps_category": nps_category,
                "key_phrases": []
            })

        return {"comments": results}

    def _detect_basic_pain_point(self, comment: str) -> Optional[str]:
        """Basic keyword-based pain point detection for fallback."""
        comment_lower = comment.lower()

        pain_keywords = {
            "precio": ["caro", "precio", "cost", "expensive", "barato"],
            "calidad": ["calidad", "malo", "roto", "defect", "quality"],
            "servicio": ["servicio", "atencion", "personal", "service"],
            "tiempo": ["demora", "tarde", "espera", "lento", "slow", "wait"],
            "app": ["app", "aplicacion", "sistema", "bug", "error"]
        }

        for category, keywords in pain_keywords.items():
            if any(word in comment_lower for word in keywords):
                return category

        return None