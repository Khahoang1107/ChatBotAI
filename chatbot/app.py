from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
import asyncio
from handlers.chat_handler import ChatHandler
from handlers.hybrid_chat_handler import HybridChatBot
from handlers.rasa_handler import RasaChatHandler
from utils.logger import setup_logger

app = Flask(__name__)
CORS(app)  # Cho phép frontend kết nối

# Setup logging
logger = setup_logger()

# Khởi tạo chat handlers
chat_handler = ChatHandler()  # Original handler
hybrid_chat = HybridChatBot()  # Hybrid system
rasa_chat = RasaChatHandler()  # Rasa-first handler

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái service"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "chatbot",
        "features": {
            "rasa_enabled": True,
            "openai_enabled": True,
            "hybrid_mode": True
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Xử lý tin nhắn với Rasa làm engine chính"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing message in request"
            }), 400

        user_message = data['message']
        user_id = data.get('user_id', 'anonymous')
        use_rasa_primary = data.get('use_rasa_primary', True)  # Rasa làm chính
        
        # Log tin nhắn đến
        logger.info(f"Received message from {user_id}: {user_message}")
        
        if use_rasa_primary:
            # Sử dụng Rasa làm engine chính
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                rasa_chat.process_message(user_message, user_id)
            )
            loop.close()
        else:
            # Fallback to original handler (now also supports Rasa with hybrid fallback)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response = loop.run_until_complete(
                chat_handler.process_message(user_message, user_id)
            )
            loop.close()
        
        # Log phản hồi
        logger.info(f"Bot response to {user_id}: {response.get('message', '')[:100]}...")
        
        return jsonify({
            "message": response.get('message', ''),
            "type": response.get('type', 'text'),
            "timestamp": datetime.datetime.now().isoformat(),
            "suggestions": response.get('suggestions', []),
            "method": response.get('method', 'unknown'),
            "intent": response.get('intent'),
            "confidence": response.get('confidence'),
            "entities": response.get('entities', [])
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau.",
            "timestamp": datetime.datetime.now().isoformat(),
            "suggestions": [
                "Thử lại",
                "Liên hệ hỗ trợ",
                "Sử dụng chế độ đơn giản"
            ]
        }), 500

@app.route('/chat/simple', methods=['POST'])
def chat_simple():
    """Endpoint cho chat đơn giản (không dùng Rasa)"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing message in request"
            }), 400

        user_message = data['message']
        user_id = data.get('user_id', 'anonymous')
        
        # Sử dụng original chat handler
        response = chat_handler.process_message(user_message, user_id)
        
        return jsonify({
            "message": response.get('message', ''),
            "type": response.get('type', 'text'),
            "timestamp": datetime.datetime.now().isoformat(),
            "suggestions": response.get('suggestions', []),
            "method": "simple"
        })
        
    except Exception as e:
        logger.error(f"Error in simple chat: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau."
        }), 500

@app.route('/rasa/status', methods=['GET'])
def rasa_status():
    """Kiểm tra trạng thái Rasa server"""
    try:
        import requests
        response = requests.get('http://localhost:5005/status', timeout=5)
        return jsonify({
            "rasa_status": "online",
            "rasa_response": response.json()
        })
    except Exception as e:
        return jsonify({
            "rasa_status": "offline", 
            "error": str(e)
        })

@app.route('/ai/test', methods=['POST'])
def test_ai():
    """Test endpoint để kiểm tra AI functionality"""
    try:
        data = request.get_json()
        message = data.get('message', 'Hello')
        
        # Test với hybrid system
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            hybrid_chat.process_message(message, 'test_user')
        )
        loop.close()
        
        return jsonify({
            "test_message": message,
            "ai_response": response,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI test error: {str(e)}")
        return jsonify({
            "error": str(e)
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook cho tích hợp với các platform khác"""
    try:
        data = request.get_json()
        logger.info(f"Webhook received: {data}")
        
        # Xử lý webhook data
        # Có thể tích hợp với Telegram, Facebook Messenger, etc.
        
        return jsonify({"status": "received"})
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "Webhook processing failed"}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Lấy thống kê chatbot"""
    try:
        stats = chat_handler.get_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Stats error: {str(e)}")
        return jsonify({"error": "Failed to get statistics"}), 500

if __name__ == '__main__':
    print("🤖 Starting Hybrid AI Chatbot...")
    print("📡 Server running on http://localhost:5001")
    print("🔗 Health check: http://localhost:5001/health")
    print("🧠 AI Test: POST http://localhost:5001/ai/test")
    print("💬 Chat: POST http://localhost:5001/chat")
    print("🔧 Rasa Status: GET http://localhost:5001/rasa/status")
    
    logger.info("Starting Hybrid AI Chatbot Service...")
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )