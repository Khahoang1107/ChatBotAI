"""
Hybrid Chat Routes
Routes để frontend gọi tới hybrid chat system
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import logging
from services.hybrid_chat_service import HybridChatService

logger = logging.getLogger(__name__)

# Tạo Blueprint
hybrid_chat_bp = Blueprint('hybrid_chat', __name__)

# Khởi tạo service
hybrid_service = HybridChatService()

@hybrid_chat_bp.route('/chat', methods=['POST'])
@jwt_required()
def send_message():
    """
    Endpoint để frontend gửi tin nhắn tới hybrid system
    
    Request body:
    {
        "message": "Tin nhắn từ user",
        "conversation_id": "optional - để track conversation"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "message": "Tin nhắn gốc",
            "response": "Phản hồi từ system",
            "source": "rasa|chatbot|fallback|error",
            "confidence": 0.8,
            "timestamp": "ISO timestamp",
            "user_id": "user_id"
        }
    }
    """
    try:
        # Lấy user ID từ JWT token
        current_user = get_jwt_identity()
        
        # Lấy data từ request
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Sử dụng conversation_id nếu có, không thì dùng user_id
        conversation_id = data.get('conversation_id', current_user)
        
        logger.info(f"Received chat message from user {current_user}: {message}")
        
        # Gửi tin nhắn thông qua hybrid service
        response = hybrid_service.send_message(message, conversation_id)
        
        # Thêm user_id vào response
        response['user_id'] = current_user
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except Exception as e:
        logger.error(f"Error in hybrid chat endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "Đã có lỗi xảy ra khi xử lý tin nhắn"
        }), 500

@hybrid_chat_bp.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint kiểm tra trạng thái health của hybrid system
    
    Response:
    {
        "success": true,
        "data": {
            "timestamp": "ISO timestamp",
            "rasa": {
                "status": "healthy|unhealthy|error",
                "response_time": "0.123s"
            },
            "chatbot": {
                "status": "healthy|unhealthy|error", 
                "response_time": "0.456s"
            }
        }
    }
    """
    try:
        health_status = hybrid_service.get_health_status()
        
        # Determine overall health
        rasa_healthy = health_status['rasa']['status'] == 'healthy'
        chatbot_healthy = health_status['chatbot']['status'] == 'healthy'
        
        overall_status = "healthy" if (rasa_healthy or chatbot_healthy) else "unhealthy"
        
        return jsonify({
            "success": True,
            "overall_status": overall_status,
            "data": health_status
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Health check failed",
            "message": str(e)
        }), 500

@hybrid_chat_bp.route('/chat/anonymous', methods=['POST'])
def send_message_anonymous():
    """
    Endpoint cho guest users (không cần authentication)
    
    Request body:
    {
        "message": "Tin nhắn từ user",
        "session_id": "optional - để track session"
    }
    """
    try:
        # Lấy data từ request
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "error": "No JSON data provided"
            }), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({
                "success": False,
                "error": "Message is required"
            }), 400
        
        # Sử dụng session_id hoặc tạo anonymous ID
        session_id = data.get('session_id', f"anonymous_{request.remote_addr}")
        
        logger.info(f"Received anonymous chat message: {message}")
        
        # Gửi tin nhắn thông qua hybrid service
        response = hybrid_service.send_message(message, session_id)
        
        return jsonify({
            "success": True,
            "data": response
        }), 200
        
    except Exception as e:
        logger.error(f"Error in anonymous chat endpoint: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "message": "Đã có lỗi xảy ra khi xử lý tin nhắn"
        }), 500

@hybrid_chat_bp.route('/conversation/<conversation_id>', methods=['GET'])
@jwt_required()
def get_conversation_history(conversation_id):
    """
    Lấy lịch sử conversation (có thể implement sau)
    """
    try:
        # TODO: Implement conversation history retrieval
        return jsonify({
            "success": True,
            "data": {
                "conversation_id": conversation_id,
                "messages": [],
                "message": "Conversation history not implemented yet"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get conversation history"
        }), 500

@hybrid_chat_bp.route('/config', methods=['GET'])
def get_config():
    """
    Lấy thông tin cấu hình của hybrid system
    """
    try:
        config_info = {
            "rasa_url": hybrid_service.rasa_url,
            "chatbot_url": hybrid_service.chatbot_url,
            "confidence_threshold": hybrid_service.confidence_threshold,
            "request_timeout": hybrid_service.request_timeout,
            "features": {
                "rasa_integration": True,
                "chatbot_fallback": True,
                "anonymous_chat": True,
                "authenticated_chat": True,
                "health_monitoring": True
            }
        }
        
        return jsonify({
            "success": True,
            "data": config_info
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting config: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Failed to get config"
        }), 500