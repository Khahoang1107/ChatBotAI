"""
Sentiment Analysis Service
Analyzes user messages for sentiment and adjusts chatbot responses accordingly
"""

import re
from typing import Dict, Any, Tuple
from textblob import TextBlob
import os

class SentimentService:
    """Service for analyzing sentiment in user messages"""

    def __init__(self):
        # Vietnamese sentiment keywords
        self.positive_words = {
            'tốt', 'hay', 'tuyệt', 'xuất sắc', 'tuyệt vời', 'thích', 'yêu thích',
            'hài lòng', 'vui', 'vui vẻ', 'hạnh phúc', 'tích cực', 'tốt lành',
            'hoàn hảo', 'đỉnh', 'pro', 'ngon', 'đẹp', 'xinh', 'tươi',
            'cảm ơn', 'thank', 'thanks', 'good', 'great', 'excellent', 'awesome'
        }

        self.negative_words = {
            'tệ', 'xấu', 'dở', 'tồi tệ', 'kinh khủng', 'tức giận', 'bực',
            'không thích', 'ghét', 'buồn', 'tuyệt vọng', 'tiêu cực', 'tồi',
            'lỗi', 'sai', 'không đúng', 'không ổn', 'bad', 'terrible', 'awful',
            'hate', 'angry', 'sad', 'disappointed', 'frustrated'
        }

        self.neutral_words = {
            'bình thường', 'ổn', 'cũng được', 'không sao', 'normal', 'okay', 'fine'
        }

    def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """
        Analyze sentiment of text
        Returns: (sentiment, confidence) where sentiment is 'positive', 'negative', or 'neutral'
        """
        try:
            # Clean text
            text = text.lower().strip()

            # Use TextBlob for basic sentiment analysis
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity

            # Vietnamese keyword-based analysis
            positive_count = sum(1 for word in self.positive_words if word in text)
            negative_count = sum(1 for word in self.negative_words if word in text)
            neutral_count = sum(1 for word in self.neutral_words if word in text)

            # Determine sentiment based on keywords and polarity
            if polarity > 0.1 or positive_count > negative_count:
                sentiment = 'positive'
                confidence = min(0.9, polarity + 0.5 + (positive_count * 0.1))
            elif polarity < -0.1 or negative_count > positive_count:
                sentiment = 'negative'
                confidence = min(0.9, abs(polarity) + 0.5 + (negative_count * 0.1))
            else:
                sentiment = 'neutral'
                confidence = 0.5 + (neutral_count * 0.1)

            return sentiment, min(confidence, 1.0)

        except Exception as e:
            print(f"Sentiment analysis error: {e}")
            return 'neutral', 0.5

    def adjust_response_based_on_sentiment(self, sentiment: str, base_response: str) -> str:
        """
        Adjust chatbot response based on user sentiment
        """
        if sentiment == 'negative':
            # User seems frustrated - be more empathetic and helpful
            adjustments = [
                "Tôi hiểu bạn đang gặp khó khăn. ",
                "Xin lỗi nếu có gì không ổn. ",
                "Tôi sẽ hỗ trợ bạn tốt nhất có thể. ",
                "Hãy cho tôi biết thêm chi tiết để tôi giúp đỡ. "
            ]
            adjustment = adjustments[0]  # Use first adjustment
            return adjustment + base_response

        elif sentiment == 'positive':
            # User is happy - keep the positive tone
            return base_response

        else:
            # Neutral - standard response
            return base_response

    def get_sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji representing sentiment"""
        emoji_map = {
            'positive': '😊',
            'negative': '😔',
            'neutral': '😐'
        }
        return emoji_map.get(sentiment, '😐')

    def analyze_urgency(self, text: str) -> str:
        """
        Analyze urgency level in message
        Returns: 'low', 'medium', 'high'
        """
        urgency_keywords = {
            'high': ['khẩn cấp', 'gấp', 'ngay lập tức', 'urgent', 'emergency', 'asap', 'now'],
            'medium': ['sớm', 'nhanh', 'hôm nay', 'today', 'soon'],
            'low': ['khi nào cũng được', 'không vội', 'sau', 'later']
        }

        text_lower = text.lower()

        for level, keywords in urgency_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return level

        return 'medium'  # Default

    def extract_intent(self, text: str) -> str:
        """
        Extract user intent from message
        Returns intent category
        """
        intents = {
            'question': ['cái gì', 'làm thế nào', 'tại sao', 'what', 'how', 'why', '?'],
            'command': ['làm', 'tạo', 'xóa', 'cập nhật', 'do', 'create', 'delete', 'update'],
            'complaint': ['không được', 'lỗi', 'sai', 'tệ', 'xấu', 'problem', 'error', 'wrong'],
            'praise': ['tốt', 'hay', 'tuyệt', 'good', 'great', 'excellent'],
            'request': ['cần', 'muốn', 'hãy', 'please', 'can you', 'i want']
        }

        text_lower = text.lower()
        max_matches = 0
        best_intent = 'general'

        for intent, keywords in intents.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            if matches > max_matches:
                max_matches = matches
                best_intent = intent

        return best_intent

# Global sentiment service instance
sentiment_service = SentimentService()