from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import datetime
from handlers.chat_handler import ChatHandler
from utils.logger import setup_logger

app = Flask(__name__)
CORS(app)  # Cho phép frontend kết nối

# Setup logging
logger = setup_logger()

# Khởi tạo chat handler
chat_handler = ChatHandler()

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái service"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "chatbot"
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Xử lý tin nhắn từ user"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "error": "Missing message in request"
            }), 400
        
        user_message = data['message']
        user_id = data.get('user_id', 'anonymous')
        
        # Log tin nhắn đến
        logger.info(f"Received message from {user_id}: {user_message}")
        
        # Xử lý tin nhắn với AI
        response = chat_handler.process_message(user_message, user_id)
        
        # Log phản hồi
        logger.info(f"Bot response to {user_id}: {response['message']}")
        
        return jsonify({
            "message": response['message'],
            "type": response.get('type', 'text'),
            "timestamp": datetime.datetime.now().isoformat(),
            "suggestions": response.get('suggestions', [])
        })
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": "Xin lỗi, tôi gặp sự cố kỹ thuật. Vui lòng thử lại sau."
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
    logger.info("Starting Chatbot Service...")
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )