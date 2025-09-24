"""
Local sentiment analysis using VADER and TextBlob.
Fast, free alternative to OpenAI for basic emotion detection.
"""

import numpy as np
from typing import Dict, List, Optional
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import structlog

logger = structlog.get_logger()


class LocalSentimentAnalyzer:
    """Fast local sentiment analysis for basic emotions."""

    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

        # Emotion keywords for pattern matching
        self.emotion_patterns = {
            "confusion": ["no entiendo", "confuso", "no sé", "?", "unclear", "confused", "no comprendo", "no me queda claro"],
            "anticipacion": ["espero", "ojalá", "pronto", "futuro", "will", "hope", "soon", "esperando", "ansioso"],
            "enojo": ["molesto", "enojado", "furioso", "angry", "mad", "furious", "irritado", "indignado"],
            "confianza": ["confío", "seguro", "excelente", "trust", "confident", "reliable", "fiable", "confiable"]
        }

    def analyze_batch(self, comments: List[str], language: str = "es") -> List[Dict]:
        """
        Analyze emotions locally without OpenAI.

        Returns emotion scores for each comment.
        Memory efficient: processes one at a time.
        """
        results = []

        for comment in comments:
            try:
                # Translate if Spanish (TextBlob handles this efficiently)
                if language == "es":
                    blob = TextBlob(comment)
                    try:
                        # Only translate for VADER (English-only)
                        english_text = str(blob.translate(to='en'))
                        vader_scores = self.vader.polarity_scores(english_text)
                    except:
                        # Fallback if translation fails
                        vader_scores = self.vader.polarity_scores(comment)
                else:
                    vader_scores = self.vader.polarity_scores(comment)

                # Extract base sentiments
                positive = vader_scores['pos']
                negative = vader_scores['neg']
                neutral = vader_scores['neu']
                compound = vader_scores['compound']

                # Map to 7 emotions using rules
                emotions = self._map_to_emotions(
                    comment, positive, negative, neutral, compound
                )

                results.append({
                    "emotions": emotions,
                    "base_sentiment": {
                        "positive": positive,
                        "negative": negative,
                        "neutral": neutral,
                        "compound": compound
                    }
                })

            except Exception as e:
                logger.warning(f"Local sentiment failed for comment: {e}")
                # Default emotions on failure
                results.append({
                    "emotions": self._default_emotions(),
                    "base_sentiment": {"positive": 0.33, "negative": 0.33, "neutral": 0.34, "compound": 0.0}
                })

        return results

    def _map_to_emotions(self, text: str, pos: float, neg: float, neu: float, compound: float) -> Dict:
        """
        Map VADER scores to 7 specific emotions.
        Uses both scores and keyword patterns.
        """
        text_lower = text.lower()

        # Base emotion calculation from sentiment
        emotions = {
            "satisfaccion": min(1.0, pos * 1.2),  # Boost positive
            "frustracion": min(1.0, neg * 0.8),   # Slightly less than pure negative
            "enojo": 0.0,                          # Will enhance with keywords
            "confianza": 0.0,                      # Will enhance with keywords
            "decepcion": min(1.0, neg * 0.6),     # Subset of negative
            "confusion": 0.0,                      # Will enhance with patterns
            "anticipacion": 0.0                    # Will enhance with patterns
        }

        # Enhance with keyword patterns
        if any(word in text_lower for word in self.emotion_patterns["confusion"]):
            emotions["confusion"] = max(0.5, neu)
        else:
            emotions["confusion"] = neu * 0.3

        if any(word in text_lower for word in self.emotion_patterns["anticipacion"]):
            emotions["anticipacion"] = max(0.4, pos * 0.7)
        else:
            emotions["anticipacion"] = pos * 0.3

        if any(word in text_lower for word in self.emotion_patterns["enojo"]):
            emotions["enojo"] = max(emotions["frustracion"], neg * 1.2)
            emotions["frustracion"] *= 0.7  # Reduce frustration if anger detected
        else:
            emotions["enojo"] = neg * 0.4

        if any(word in text_lower for word in self.emotion_patterns["confianza"]):
            emotions["confianza"] = max(0.6, pos * 1.1)
        else:
            emotions["confianza"] = pos * 0.5 if compound > 0.5 else pos * 0.3

        # Normalize to ensure sum doesn't exceed logical bounds
        total = sum(emotions.values())
        if total > 2.5:  # Allow some overlap but not excessive
            factor = 2.5 / total
            emotions = {k: round(v * factor, 3) for k, v in emotions.items()}

        return emotions

    def _default_emotions(self) -> Dict:
        """Default neutral emotions."""
        return {
            "satisfaccion": 0.4,
            "frustracion": 0.3,
            "enojo": 0.1,
            "confianza": 0.3,
            "decepcion": 0.2,
            "confusion": 0.3,
            "anticipacion": 0.2
        }