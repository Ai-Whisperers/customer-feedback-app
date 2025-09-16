"""
OpenAI Responses API client with structured outputs.
Implements rate limiting, retries, and proper error handling.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any
import structlog
from openai import OpenAI, AsyncOpenAI
from openai.types import Response as OpenAIResponse
from tenacity import retry, stop_after_attempt, wait_exponential
import openai

from app.config import settings
from app.schemas.base import Language

logger = structlog.get_logger()


class RateLimiter:
    """Rate limiter for OpenAI API calls."""

    def __init__(self, max_rps: int = 8):
        self.max_rps = max_rps
        self.request_times = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire permission to make a request."""
        async with self.lock:
            now = time.time()
            # Remove requests older than 1 second
            self.request_times = [t for t in self.request_times if now - t < 1.0]

            # If we're at the limit, wait
            if len(self.request_times) >= self.max_rps:
                sleep_time = 1.0 - (now - self.request_times[0])
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

            # Record this request
            self.request_times.append(time.time())


class OpenAIAnalyzer:
    """OpenAI Responses API client for feedback analysis."""

    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.rate_limiter = RateLimiter(max_rps=settings.MAX_RPS)
        self.analysis_schema = self._get_analysis_schema()

    def _get_analysis_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for structured outputs."""
        return {
            "type": "object",
            "properties": {
                "comments": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {
                                "type": "integer",
                                "description": "Comment index"
                            },
                            "emotions": {
                                "type": "object",
                                "properties": {
                                    # Positive emotions
                                    "alegria": {"type": "number", "minimum": 0, "maximum": 1},
                                    "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                                    "anticipacion": {"type": "number", "minimum": 0, "maximum": 1},
                                    "sorpresa_positiva": {"type": "number", "minimum": 0, "maximum": 1},
                                    "amor": {"type": "number", "minimum": 0, "maximum": 1},
                                    "optimismo": {"type": "number", "minimum": 0, "maximum": 1},
                                    "admiracion": {"type": "number", "minimum": 0, "maximum": 1},
                                    # Negative emotions
                                    "miedo": {"type": "number", "minimum": 0, "maximum": 1},
                                    "tristeza": {"type": "number", "minimum": 0, "maximum": 1},
                                    "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                    "disgusto": {"type": "number", "minimum": 0, "maximum": 1},
                                    "sorpresa_negativa": {"type": "number", "minimum": 0, "maximum": 1},
                                    "verguenza": {"type": "number", "minimum": 0, "maximum": 1},
                                    "culpa": {"type": "number", "minimum": 0, "maximum": 1},
                                    # Neutral emotions
                                    "interes": {"type": "number", "minimum": 0, "maximum": 1},
                                    "confusion": {"type": "number", "minimum": 0, "maximum": 1}
                                },
                                "required": [
                                    "alegria", "confianza", "anticipacion", "sorpresa_positiva",
                                    "amor", "optimismo", "admiracion", "miedo", "tristeza",
                                    "enojo", "disgusto", "sorpresa_negativa", "verguenza",
                                    "culpa", "interes", "confusion"
                                ],
                                "additionalProperties": False
                            },
                            "churn_risk": {
                                "type": "number",
                                "minimum": 0,
                                "maximum": 1,
                                "description": "Probability of customer churn (0-1)"
                            },
                            "pain_points": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "minLength": 2,
                                    "maxLength": 50
                                },
                                "maxItems": 5,
                                "description": "Key issues mentioned"
                            },
                            "sentiment": {
                                "type": "string",
                                "enum": ["muy_positivo", "positivo", "neutral", "negativo", "muy_negativo"]
                            },
                            "language": {
                                "type": "string",
                                "enum": ["es", "en"]
                            }
                        },
                        "required": ["id", "emotions", "churn_risk", "pain_points", "sentiment", "language"],
                        "additionalProperties": False
                    }
                },
                "batch_summary": {
                    "type": "object",
                    "properties": {
                        "total_analyzed": {"type": "integer", "minimum": 0},
                        "avg_sentiment_score": {"type": "number", "minimum": -1, "maximum": 1},
                        "main_concerns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "maxItems": 10
                        }
                    },
                    "required": ["total_analyzed", "avg_sentiment_score", "main_concerns"],
                    "additionalProperties": False
                }
            },
            "required": ["comments", "batch_summary"],
            "additionalProperties": False
        }

    def _build_instructions(self, language_hint: Optional[Language] = None) -> str:
        """Build system instructions for analysis."""
        base_instructions = """
        Eres un experto analista de feedback de clientes. Tu tarea es analizar comentarios
        y extraer información estructurada sobre emociones, riesgo de churn y pain points.

        INSTRUCCIONES DETALLADAS:

        1. EMOCIONES (16 estados):
           - Asigna probabilidades 0-1 para cada emoción
           - Pueden coexistir múltiples emociones (no suman 1)
           - Considera matices sutiles y contexto
           - Detecta sarcasmo y ajusta en consecuencia

        2. CHURN RISK (0-1):
           - 0.8-1.0: Menciones explícitas de cancelar, cambiar proveedor
           - 0.6-0.8: Frustración alta, comparaciones con competencia
           - 0.4-0.6: Insatisfacción moderada, quejas específicas
           - 0.2-0.4: Críticas constructivas, sugerencias
           - 0.0-0.2: Satisfacción, lealtad, recomendaciones

        3. PAIN POINTS:
           - Máximo 5 por comentario
           - Usa términos específicos (ej: "tiempo_espera" no "problema")
           - En idioma original del comentario
           - Solo problemas reales mencionados

        4. SENTIMENT:
           - muy_positivo: Elogios, recomendaciones, amor por la marca
           - positivo: Satisfacción general, aspectos positivos
           - neutral: Comentarios informativos, sin valencia clara
           - negativo: Quejas, insatisfacción, problemas
           - muy_negativo: Rechazo total, experiencias terrible

        5. LANGUAGE:
           - Detecta si es español (es) o inglés (en)
           - Considera palabras clave y estructuras gramaticales

        IMPORTANTE:
        - Mantén objetividad absoluta
        - No inventes información no presente
        - Respeta el formato JSON Schema exacto
        - Cada comentario debe tener su análisis completo
        """

        if language_hint:
            base_instructions += f"\n\nHINT: La mayoría de comentarios están en {language_hint.value}"

        return base_instructions

    def _format_comments_input(self, comments: List[str]) -> str:
        """Format comments for analysis."""
        formatted = []
        for idx, comment in enumerate(comments):
            formatted.append(f"[{idx}] {comment}")
        return "\n\n".join(formatted)

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
            instructions = self._build_instructions(language_hint)
            input_text = self._format_comments_input(comments)

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

    def estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        # Rough estimation: 1 token ≈ 4 characters for Spanish/English
        return len(text) // 4

    def optimize_batch_size(
        self,
        comments: List[str],
        max_tokens: int = 3500
    ) -> List[List[str]]:
        """
        Optimize batch sizes based on token estimates.

        Args:
            comments: List of comments to batch
            max_tokens: Maximum tokens per batch

        Returns:
            List of comment batches
        """
        batches = []
        current_batch = []
        current_tokens = 0

        # Reserve tokens for instructions and response
        available_tokens = max_tokens - 1000

        for comment in comments:
            comment_tokens = self.estimate_tokens(comment)

            # If adding this comment would exceed the limit, start new batch
            if (current_tokens + comment_tokens > available_tokens and
                len(current_batch) > 0):
                batches.append(current_batch)
                current_batch = [comment]
                current_tokens = comment_tokens
            else:
                current_batch.append(comment)
                current_tokens += comment_tokens

            # Hard limit on batch size
            if len(current_batch) >= settings.MAX_BATCH_SIZE:
                batches.append(current_batch)
                current_batch = []
                current_tokens = 0

        # Add remaining comments
        if current_batch:
            batches.append(current_batch)

        logger.info(
            "Optimized batching",
            total_comments=len(comments),
            total_batches=len(batches),
            avg_batch_size=len(comments) / len(batches) if batches else 0
        )

        return batches


# Global instance
openai_analyzer = OpenAIAnalyzer()