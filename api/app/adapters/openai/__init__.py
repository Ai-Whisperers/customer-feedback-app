"""
OpenAI adapter package.
Provides structured AI analysis for customer feedback.
"""

from app.adapters.openai.analyzer import OpenAIAnalyzer

# Create singleton instance
openai_analyzer = OpenAIAnalyzer()

__all__ = ["openai_analyzer", "OpenAIAnalyzer"]