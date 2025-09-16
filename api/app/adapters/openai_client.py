"""
OpenAI client adapter - compatibility wrapper.
This module maintains backward compatibility while using the new modular structure.
"""

from app.adapters.openai import openai_analyzer

# Export for backward compatibility
__all__ = ["openai_analyzer"]