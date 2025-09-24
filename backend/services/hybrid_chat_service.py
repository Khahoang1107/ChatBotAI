"""
Hybrid Chat Service
Service này sẽ xử lý logic giao tiếp với Rasa trước, nếu không được thì fallback sang Chatbot
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class HybridChatService:
    """
    Service xử lý logic hybrid chat:
    1. Gửi request tới Rasa trước
    2. Nếu Rasa không xử lý được hoặc lỗi, fallback sang Chatbot
    3. Trả về response tốt nhất
    """
    
    def __init__(self):
        # Cấu hình các service endpoints
        self.rasa_url = "http://rasa:5005"  # Rasa service trong Docker
        self.chatbot_url = "http://chatbot:5001"  # Chatbot service trong Docker
        
        # Timeout cho các request
        self.request_timeout = 10
        
        # Threshold để quyết định response có tốt không
        self.confidence_threshold = 0.7
        
        # History để track conversation
        self.conversation_history = {}
    
    def send_message(self, message: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Gửi tin nhắn thông qua hybrid system
        
        Args:
            message: Tin nhắn từ user
            user_id: ID của user (để track conversation)
            
        Returns:
            Response từ system tốt nhất
        """
        logger.info(f"Processing message for user {user_id}: {message}")
        
        # Chuẩn bị response structure
        response = {
            "message": message,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "source": None,
            "response": None,
            "confidence": 0.0,
            "success": False,
            "error": None
        }
        
        try:
            # Bước 1: Thử với Rasa trước
            rasa_response = self._try_rasa(message, user_id)
            
            if rasa_response and self._is_good_response(rasa_response):
                logger.info("Rasa provided good response")
                response.update({
                    "source": "rasa",
                    "response": rasa_response.get("response", ""),
                    "confidence": rasa_response.get("confidence", 0.0),
                    "success": True,
                    "rasa_intent": rasa_response.get("intent", {}),
                    "rasa_entities": rasa_response.get("entities", [])
                })
                return response
            
            # Bước 2: Fallback sang Chatbot
            logger.info("Rasa response not good enough, trying chatbot")
            chatbot_response = self._try_chatbot(message, user_id)
            
            if chatbot_response and chatbot_response.get("success"):
                logger.info("Chatbot provided response")
                response.update({
                    "source": "chatbot", 
                    "response": chatbot_response.get("response", ""),
                    "confidence": chatbot_response.get("confidence", 0.8),
                    "success": True,
                    "chatbot_data": chatbot_response.get("data", {})
                })
                return response
            
            # Bước 3: Nếu cả hai đều fail
            logger.warning("Both Rasa and Chatbot failed")
            response.update({
                "source": "fallback",
                "response": "Xin lỗi, tôi không thể xử lý câu hỏi này. Vui lòng thử lại hoặc liên hệ hỗ trợ.",
                "confidence": 0.1,
                "success": False,
                "error": "Both services failed to provide response"
            })
            
        except Exception as e:
            logger.error(f"Error in hybrid chat service: {str(e)}")
            response.update({
                "source": "error",
                "response": "Đã có lỗi xảy ra. Vui lòng thử lại sau.",
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            })
        
        return response
    
    def _try_rasa(self, message: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Thử gửi tin nhắn tới Rasa
        
        Returns:
            Response từ Rasa hoặc None nếu lỗi
        """
        try:
            payload = {
                "sender": user_id,
                "message": message
            }
            
            response = requests.post(
                f"{self.rasa_url}/webhooks/rest/webhook",
                json=payload,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                rasa_data = response.json()
                logger.debug(f"Rasa response: {rasa_data}")
                
                if rasa_data and isinstance(rasa_data, list) and len(rasa_data) > 0:
                    # Rasa trả về list, lấy response đầu tiên
                    first_response = rasa_data[0]
                    
                    # Lấy thêm thông tin intent và entities nếu có
                    intent_info = self._get_rasa_intent(message, user_id)
                    
                    return {
                        "response": first_response.get("text", ""),
                        "confidence": intent_info.get("confidence", 0.5),
                        "intent": intent_info.get("intent", {}),
                        "entities": intent_info.get("entities", []),
                        "raw_response": rasa_data
                    }
            
            logger.warning(f"Rasa returned status {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.warning("Rasa request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning("Cannot connect to Rasa")
            return None
        except Exception as e:
            logger.error(f"Error calling Rasa: {str(e)}")
            return None
    
    def _get_rasa_intent(self, message: str, user_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin intent từ Rasa NLU
        """
        try:
            payload = {
                "text": message
            }
            
            response = requests.post(
                f"{self.rasa_url}/model/parse",
                json=payload,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            logger.error(f"Error getting Rasa intent: {str(e)}")
        
        return {"intent": {}, "entities": [], "confidence": 0.0}
    
    def _try_chatbot(self, message: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Thử gửi tin nhắn tới Chatbot
        
        Returns:
            Response từ Chatbot hoặc None nếu lỗi
        """
        try:
            payload = {
                "message": message,
                "user_id": user_id
            }
            
            response = requests.post(
                f"{self.chatbot_url}/chat",
                json=payload,
                timeout=self.request_timeout
            )
            
            if response.status_code == 200:
                chatbot_data = response.json()
                logger.debug(f"Chatbot response: {chatbot_data}")
                return chatbot_data
            
            logger.warning(f"Chatbot returned status {response.status_code}")
            return None
            
        except requests.exceptions.Timeout:
            logger.warning("Chatbot request timeout")
            return None
        except requests.exceptions.ConnectionError:
            logger.warning("Cannot connect to Chatbot")
            return None
        except Exception as e:
            logger.error(f"Error calling Chatbot: {str(e)}")
            return None
    
    def _is_good_response(self, rasa_response: Dict[str, Any]) -> bool:
        """
        Kiểm tra xem response từ Rasa có tốt không
        
        Args:
            rasa_response: Response từ Rasa
            
        Returns:
            True nếu response tốt, False nếu không
        """
        if not rasa_response:
            return False
        
        # Kiểm tra confidence threshold
        confidence = rasa_response.get("confidence", 0.0)
        if confidence < self.confidence_threshold:
            logger.debug(f"Rasa confidence {confidence} below threshold {self.confidence_threshold}")
            return False
        
        # Kiểm tra có response text không
        response_text = rasa_response.get("response", "").strip()
        if not response_text:
            logger.debug("Rasa response empty")
            return False
        
        # Kiểm tra intent có phải là nlu_fallback không
        intent = rasa_response.get("intent", {})
        intent_name = intent.get("name", "")
        if intent_name == "nlu_fallback":
            logger.debug("Rasa returned fallback intent")
            return False
        
        return True
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Kiểm tra trạng thái health của các services
        
        Returns:
            Dict chứa trạng thái của Rasa và Chatbot
        """
        health = {
            "timestamp": datetime.now().isoformat(),
            "rasa": {"status": "unknown", "response_time": None},
            "chatbot": {"status": "unknown", "response_time": None}
        }
        
        # Check Rasa
        try:
            start_time = time.time()
            response = requests.get(f"{self.rasa_url}/status", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health["rasa"] = {
                    "status": "healthy",
                    "response_time": f"{response_time:.3f}s",
                    "data": response.json()
                }
            else:
                health["rasa"]["status"] = f"unhealthy (status: {response.status_code})"
        except Exception as e:
            health["rasa"]["status"] = f"error: {str(e)}"
        
        # Check Chatbot
        try:
            start_time = time.time()
            response = requests.get(f"{self.chatbot_url}/health", timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health["chatbot"] = {
                    "status": "healthy", 
                    "response_time": f"{response_time:.3f}s",
                    "data": response.json()
                }
            else:
                health["chatbot"]["status"] = f"unhealthy (status: {response.status_code})"
        except Exception as e:
            health["chatbot"]["status"] = f"error: {str(e)}"
        
        return health