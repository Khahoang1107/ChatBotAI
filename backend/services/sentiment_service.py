# Sentiment Service using HuggingFace Transformers
from transformers import pipeline
from typing import Dict

class SentimentService:
    def __init__(self):
        self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

    def analyze(self, text: str) -> Dict:
        """Analyze sentiment of the input text."""
        result = self.analyzer(text)[0]
        # result: {'label': 'POSITIVE'/'NEGATIVE', 'score': float}
        return {
            "label": result["label"],
            "score": result["score"]
        }

# Singleton instance
sentiment_service = SentimentService()