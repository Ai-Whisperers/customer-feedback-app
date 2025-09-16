"""
OpenAI schemas and prompts for structured outputs.
"""

from typing import Dict, Any, Optional
from app.schemas.base import Language


def get_analysis_schema() -> Dict[str, Any]:
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


def build_analysis_instructions(language_hint: Optional[Language] = None) -> str:
    """
    Build system instructions for analysis.

    Args:
        language_hint: Optional language hint for better analysis

    Returns:
        System instructions string
    """
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