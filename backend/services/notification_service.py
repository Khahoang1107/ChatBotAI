"""
Notification Service for Event-Driven notifications
"""
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import redis
import os

logger = logging.getLogger(__name__)

class NotificationService:
    """
    Service to handle real-time notifications via WebSocket, Redis Pub/Sub
    """
    
    def __init__(self):
        # Redis connection for pub/sub
        redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        
        # Notification channels
        self.channels = {
            'ocr_completed': 'notifications:ocr:completed',
            'ocr_failed': 'notifications:ocr:failed',
            'ai_training': 'notifications:ai:training',
            'system': 'notifications:system'
        }
    
    def send_notification(self, type: str, message: str, data: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None):
        """
        Send notification via Redis pub/sub
        
        Args:
            type: Notification type (ocr_completed, ocr_failed, etc.)
            message: Human-readable message
            data: Additional data payload
            user_id: Target user (optional, for targeted notifications)
        """
        try:
            notification_payload = {
                'type': type,
                'message': message,
                'data': data or {},
                'timestamp': datetime.now().isoformat(),
                'user_id': user_id
            }
            
            # Get appropriate channel
            channel = self.channels.get(type, self.channels['system'])
            
            # If user_id is specified, send to user-specific channel
            if user_id:
                channel = f"{channel}:user:{user_id}"
            
            # Publish to Redis
            self.redis_client.publish(channel, json.dumps(notification_payload))
            
            # Also store in a list for history (last 100 notifications)
            history_key = f"notification_history:{type}"
            self.redis_client.lpush(history_key, json.dumps(notification_payload))
            self.redis_client.ltrim(history_key, 0, 99)  # Keep only last 100
            
            logger.info(f"Notification sent: {type} - {message}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return False
    
    def send_ocr_completion_notification(self, ocr_result_id: int, confidence_score: float, processing_time: float, user_id: Optional[str] = None):
        """
        Send OCR completion notification
        """
        if confidence_score >= 0.7:
            message = f"🎉 OCR completed successfully with {confidence_score:.1%} confidence in {processing_time:.1f}s"
            type = "ocr_completed"
        else:
            message = f"⚠️ OCR completed with low confidence ({confidence_score:.1%}) in {processing_time:.1f}s"
            type = "ocr_completed"
        
        data = {
            'ocr_result_id': ocr_result_id,
            'confidence_score': confidence_score,
            'processing_time': processing_time,
            'success': True
        }
        
        return self.send_notification(type, message, data, user_id)
    
    def send_ocr_failure_notification(self, ocr_result_id: int, error_message: str, user_id: Optional[str] = None):
        """
        Send OCR failure notification
        """
        message = f"❌ OCR processing failed: {error_message}"
        
        data = {
            'ocr_result_id': ocr_result_id,
            'error_message': error_message,
            'success': False
        }
        
        return self.send_notification("ocr_failed", message, data, user_id)
    
    def send_ai_training_notification(self, training_id: int, status: str, message: str, user_id: Optional[str] = None):
        """
        Send AI training notification
        """
        data = {
            'training_id': training_id,
            'status': status
        }
        
        return self.send_notification("ai_training", message, data, user_id)
    
    def get_notification_history(self, type: str, limit: int = 20) -> list:
        """
        Get notification history for a specific type
        """
        try:
            history_key = f"notification_history:{type}"
            notifications = self.redis_client.lrange(history_key, 0, limit - 1)
            return [json.loads(notif) for notif in notifications]
        except Exception as e:
            logger.error(f"Failed to get notification history: {str(e)}")
            return []
    
    def subscribe_to_notifications(self, user_id: Optional[str] = None):
        """
        Subscribe to notifications (for WebSocket connections)
        """
        pubsub = self.redis_client.pubsub()
        
        # Subscribe to general channels
        channels = list(self.channels.values())
        
        # Subscribe to user-specific channels if user_id provided
        if user_id:
            user_channels = [f"{channel}:user:{user_id}" for channel in channels]
            channels.extend(user_channels)
        
        pubsub.subscribe(*channels)
        return pubsub
    
    def send_system_notification(self, message: str, level: str = "info", data: Optional[Dict[str, Any]] = None):
        """
        Send system-wide notification
        """
        data = data or {}
        data['level'] = level
        
        icon = "ℹ️" if level == "info" else "⚠️" if level == "warning" else "❌"
        formatted_message = f"{icon} {message}"
        
        return self.send_notification("system", formatted_message, data)


# Singleton instance
notification_service = NotificationService()