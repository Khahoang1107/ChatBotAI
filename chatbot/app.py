from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, send
import json
import datetime
import asyncio
import requests
from handlers.chat_handler import ChatHandler
from handlers.hybrid_chat_handler import HybridChatBot
from utils.logger import setup_logger

app = Flask(__name__)
CORS(app, origins=["http://localhost:3001", "http://localhost:3000"])  # Cho phép frontend kết nối

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3001", "http://localhost:3000"])

# Store active WebSocket connections
active_connections = set()

# Setup logging
logger = setup_logger()

# Khởi tạo chat handlers
chat_handler = ChatHandler()  # Pattern-based handler
hybrid_chat = HybridChatBot()  # Hybrid system

@app.route('/', methods=['GET'])
def home():
    """Trang chủ chatbot service"""
    return jsonify({
        "message": "Chatbot Service API",
        "version": "1.0.0", 
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
            "hybrid_chat": "/hybrid_chat"
        },
        "documentation": "Send POST requests to /chat with JSON: {'message': 'your message'}"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Kiểm tra trạng thái service"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "chatbot",
        "features": {
            "rasa_enabled": False,
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
        # Log tin nhắn đến
        logger.info(f"Received message from {user_id}: {user_message}")
        
        # Sử dụng pattern-based handler
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
            "entities": response.get('entities', []),
            "action": response.get('action'),  # ⭐ THÊM ACTION
            "ocr_mode": response.get('ocr_mode', False)  # ⭐ THÊM OCR MODE
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

# Rasa status endpoint removed - using pattern-based system only

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

@app.route('/upload-image', methods=['POST'])
def upload_image():
    """Upload và xử lý OCR ảnh"""
    try:
        if 'image' not in request.files:
            return jsonify({
                "error": "No image file provided",
                "message": "Vui lòng chọn file ảnh để upload."
            }), 400
        
        file = request.files['image']
        user_id = request.form.get('user_id', 'anonymous')
        
        if file.filename == '':
            return jsonify({
                "error": "No file selected", 
                "message": "Chưa chọn file nào."
            }), 400
        
        # Kiểm tra file type
        allowed_extensions = ['.png', '.jpg', '.jpeg', '.pdf', '.gif']
        file_ext = '.' + file.filename.split('.')[-1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({
                "error": "Invalid file type",
                "message": f"File không được hỗ trợ. Chỉ chấp nhận: {', '.join(allowed_extensions)}"
            }), 400
        
        # Read file content
        file_content = file.read()
        file.seek(0)  # Reset file pointer
        
        # Gọi OCR backend để xử lý
        import requests
        
        # Prepare file for backend - tạo lại file object
        files = {'file': (file.filename, file_content, file.mimetype or 'application/octet-stream')}
        data = {'confidence_threshold': 0.7}
        
        logger.info(f"Sending file {file.filename} ({len(file_content)} bytes) to backend OCR")
        
        # Call backend OCR API
        backend_response = requests.post(
            'http://localhost:8000/api/ocr/camera-ocr',
            files=files,
            data=data,
            timeout=30
        )
        
        if backend_response.status_code == 200:
            ocr_result = backend_response.json()
            
            # Sử dụng chat handler để tạo notification
            from handlers.chat_handler import ChatHandler
            handler = ChatHandler()
            
            # Tạo notification tự động
            notification_response = handler.notify_file_processed(file.filename, ocr_result)
            
            logger.info(f"OCR processed successfully for user {user_id}")
            
            return jsonify({
                "message": notification_response.get('message'),
                "type": notification_response.get('type', 'ocr_result'), 
                "ocr_data": ocr_result,
                "suggestions": notification_response.get('suggestions', [
                    "Xem chi tiết đầy đủ",
                    "Tạo template", 
                    "Chụp ảnh khác",
                    "Danh sách hóa đơn"
                ]),
                "auto_notify": True,
                "timestamp": datetime.datetime.now().isoformat()
            })
            
        else:
            logger.error(f"Backend OCR failed: {backend_response.status_code}")
            return jsonify({
                "error": "OCR processing failed",
                "message": f"⚠️ Không thể xử lý ảnh. Lỗi: {backend_response.text}",
                "suggestions": [
                    "Thử ảnh khác",
                    "Kiểm tra chất lượng ảnh", 
                    "Liên hệ hỗ trợ"
                ]
            }), 500
            
    except Exception as e:
        logger.error(f"Upload image error: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": f"⚠️ Lỗi khi xử lý ảnh: {str(e)}",
            "suggestions": [
                "Thử lại",
                "Kiểm tra kết nối",
                "Liên hệ hỗ trợ"
            ]
        }), 500

@app.route('/notify-ocr-complete', methods=['POST'])
def notify_ocr_complete():
    """Endpoint để backend notify chatbot khi OCR hoàn thành"""
    try:
        data = request.get_json()
        
        if not data or 'ocr_data' not in data:
            return jsonify({
                "error": "Missing OCR data in request"
            }), 400

        ocr_data = data['ocr_data']
        user_id = data.get('user_id', 'anonymous')
        filename = ocr_data.get('filename', 'unknown')
        invoice_type = ocr_data.get('invoice_type', 'unknown')
        buyer_name = ocr_data.get('buyer_name', 'N/A')
        total_amount = ocr_data.get('total_amount', 'N/A')
        
        logger.info(f"🔔 OCR completion notification for file: {filename}")
        
        # Tạo detailed notification message
        notification_msg = f"""✅ **OCR Processing Completed Successfully!**

📄 **File**: {filename}
📋 **Type**: {invoice_type}
👤 **Buyer**: {buyer_name}  
💰 **Amount**: {total_amount}
⏱️ **Time**: {datetime.datetime.now().strftime('%H:%M:%S')}

🤖 Chatbot đã nhận được thông tin và sẵn sàng trả lời câu hỏi về hóa đơn này."""
        
        # Gửi notification qua WebSocket tới tất cả clients đang kết nối
        socketio.emit('ocr_notification', {
            'type': 'ocr_notification',
            'message': notification_msg,
            'ocr_data': ocr_data,
            'timestamp': datetime.datetime.now().isoformat(),
            'filename': filename,
            'status': 'success'
        })
        
        # Gửi notification qua chat handler (backup)
        notification_response = chat_handler.notify_file_processed(filename, ocr_data)
        
        logger.info(f"📡 WebSocket notification sent to {len(active_connections)} clients")
        
        return jsonify({
            "status": "notified",
            "message": notification_response.get('message'),
            "websocket_sent": True,
            "clients_notified": len(active_connections),
            "type": "ocr_completion",
            "ocr_data": ocr_data,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"OCR notification error: {str(e)}")
        return jsonify({
            "error": "Failed to send notification",
            "details": str(e)
        }), 500

@app.route('/process-file', methods=['POST'])
def process_file_notification():
    """Endpoint để xử lý file và trả về notification ngay lập tức"""
    try:
        data = request.get_json()
        
        if not data or 'filename' not in data:
            return jsonify({
                "error": "Missing filename in request"
            }), 400

        filename = data['filename'] 
        user_id = data.get('user_id', 'anonymous')
        
        logger.info(f"Processing file notification for: {filename}")
        
        # Sử dụng chat handler để xử lý như một message
        from handlers.chat_handler import ChatHandler
        handler = ChatHandler()
        
        # Tạo message với filename để trigger file_analysis
        message = f"xem dữ liệu từ ảnh {filename}"
        response = handler.process_message(message, user_id)
        
        return jsonify({
            "message": response.get('message', ''),
            "type": response.get('type', 'text'),
            "timestamp": datetime.datetime.now().isoformat(),
            "suggestions": response.get('suggestions', []),
            "method": "file_notification",
            "filename": filename,
            "processed": True
        })
        
    except Exception as e:
        logger.error(f"Error in process file notification: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "message": f"Lỗi xử lý thông báo file: {str(e)}"
        }), 500

if __name__ == '__main__':
    print("Starting Hybrid AI Chatbot...")
    print("Server running on http://localhost:5001")
    print("Health check: http://localhost:5001/health")
    print("AI Test: POST http://localhost:5001/ai/test")
    print("Chat: POST http://localhost:5001/chat")
    print("Upload Image: POST http://localhost:5001/upload-image")
    print("Process File: POST http://localhost:5001/process-file")
    print("WebSocket: ws://localhost:5001/socket.io/")

# ===== WebSocket Event Handlers =====

@socketio.on('connect')
def handle_connect():
    """Client WebSocket connection"""
    logger.info(f"🔗 WebSocket client connected: {request.sid}")
    active_connections.add(request.sid)
    
    # Send welcome message
    emit('connection_status', {
        'status': 'connected',
        'message': '🤖 Connected to Chatbot Service - Ready for real-time OCR notifications!',
        'timestamp': datetime.datetime.now().isoformat(),
        'client_id': request.sid
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Client WebSocket disconnection"""
    logger.info(f"❌ WebSocket client disconnected: {request.sid}")
    active_connections.discard(request.sid)

@socketio.on('ping')
def handle_ping(data):
    """Handle ping for connection testing"""
    emit('pong', {
        'message': 'pong',
        'timestamp': datetime.datetime.now().isoformat(),
        'your_data': data
    })

@socketio.on('test_notification')
def handle_test_notification(data):
    """Test endpoint for WebSocket notifications"""
    test_message = f"🧪 Test notification sent at {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    # Broadcast to all connected clients
    socketio.emit('ocr_notification', {
        'type': 'test_notification',
        'message': test_message,
        'data': data,
        'timestamp': datetime.datetime.now().isoformat()
    })
    
    logger.info(f"📡 Test notification sent to {len(active_connections)} clients")

@socketio.on('message')
def handle_message(data):
    """⭐ Handle chat messages from WebSocket"""
    try:
        logger.info(f"📩 WebSocket message received: {data}")
        
        # Extract message text
        user_message = data.get('message', '') if isinstance(data, dict) else str(data)
        user_id = data.get('user_id', request.sid) if isinstance(data, dict) else request.sid
        
        if not user_message:
            emit('error', {
                'message': 'Empty message received',
                'timestamp': datetime.datetime.now().isoformat()
            })
            return
        
        # Process message with ChatHandler
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        response = loop.run_until_complete(
            chat_handler.process_message(user_message, user_id)
        )
        loop.close()
        
        # Send response back to client
        emit('message', {
            'type': response.get('type', 'bot'),
            'message': response.get('message', ''),
            'action': response.get('action', None),  # ⭐ Include action for frontend
            'timestamp': datetime.datetime.now().isoformat(),
            'suggestions': response.get('suggestions', []),
            'ocr_mode': response.get('ocr_mode', False)
        })
        
        logger.info(f"✅ Sent response for WebSocket message: {response.get('message', '')[:50]}...")
        
    except Exception as e:
        logger.error(f"❌ WebSocket message handling error: {str(e)}")
        emit('error', {
            'message': f'Error processing message: {str(e)}',
            'timestamp': datetime.datetime.now().isoformat()
        })

if __name__ == '__main__':
    logger.info("Starting Hybrid AI Chatbot Service with WebSocket support...")
    
    # Use SocketIO run instead of app.run for WebSocket support
    socketio.run(
        app,
        host='0.0.0.0',
        port=5001,
        debug=True,
        allow_unsafe_werkzeug=True
    )