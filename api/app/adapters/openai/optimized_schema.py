"""
Optimized OpenAI JSON Schema for minimal token usage.
Single source of truth for structured outputs.
"""

from typing import Dict, Any


def get_optimized_analysis_schema() -> Dict[str, Any]:
    """
    Get optimized JSON schema for OpenAI structured outputs.
    Reduced from ~1000 chars/comment to ~150 chars/comment.
    """
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
                                "frustracion": {"type": "number", "minimum": 0, "maximum": 1},
                                "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                "satisfaccion": {"type": "number", "minimum": 0, "maximum": 1},
                                "insatisfaccion": {"type": "number", "minimum": 0, "maximum": 1},
                                "neutral": {"type": "number", "minimum": 0, "maximum": 1}
                            },
                            "required": ["frustracion", "enojo", "satisfaccion", "insatisfaccion", "neutral"],
                            "additionalProperties": False
                        },
                        "churn_risk": {
                            "type": "number",
                            "minimum": 0,
                            "maximum": 1
                        },
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
                    "required": ["emotions", "churn_risk", "pain_points", "nps"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["analyses"],
        "additionalProperties": False
    }


def get_optimized_system_prompt() -> str:
    """
    Get optimized system prompt with clear, concise instructions.
    """
    return """Analiza comentarios de clientes. Para cada uno extrae:

EMOCIONES (0-1):
- frustracion: nivel de frustración
- enojo: nivel de enojo
- satisfaccion: nivel de satisfacción
- insatisfaccion: nivel de insatisfacción
- neutral: nivel neutral/confuso

CHURN_RISK (0-1):
- 0.8-1.0: menciona cancelar/cambiar
- 0.4-0.7: quejas fuertes
- 0.0-0.3: satisfecho

PAIN_POINTS:
- Máximo 2, muy breves (<30 chars)
- Solo problemas reales mencionados

NPS:
- promoter: muy positivo (9-10)
- passive: neutral (7-8)
- detractor: negativo (0-6)

Sé preciso y objetivo. Responde solo en JSON."""


def get_optimized_user_prompt(comments: list[str], batch_index: int) -> str:
    """
    Create optimized user prompt for batch analysis.

    Args:
        comments: List of comments to analyze
        batch_index: Index of this batch

    Returns:
        Formatted prompt string
    """
    # Format comments with minimal overhead
    formatted_comments = "\n".join([
        f"{i+1}. {comment[:200]}"  # Truncate very long comments
        for i, comment in enumerate(comments)
    ])

    return f"""Analiza estos {len(comments)} comentarios:

{formatted_comments}

Responde con JSON array 'analyses' con {len(comments)} elementos en orden."""


# Example output size calculation:
# Per comment: ~150 chars
# {
#   "emotions": {"frustracion": 0.8, "enojo": 0.7, "satisfaccion": 0.1, "insatisfaccion": 0.9, "neutral": 0.1},
#   "churn_risk": 0.85,
#   "pain_points": ["servicio lento", "precio alto"],
#   "nps": "detractor"
# }
#
# 15 comments × 150 = 2,250 chars (well within limits)
# 20 comments × 150 = 3,000 chars (still safe)