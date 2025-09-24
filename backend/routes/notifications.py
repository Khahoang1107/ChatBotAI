"""
WebSocket Routes for Real-time Notifications
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import threading
from services.notification_service import NotificationService

# Create SocketIO instance (will be initialized in app.py)
socketio = None

def init_socketio(app):
    """Initialize SocketIO with Flask app"""
    global socketio
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    setup_socketio_events()
    return socketio

def setup_socketio_events():
    """Setup WebSocket event handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth=None):
        """Handle client connection"""
        print(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to notification service'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_notifications')
    def handle_join_notifications(data):
        """Join user-specific notification room"""
        try:
            user_id = data.get('user_id')
            if user_id:
                room = f"user_{user_id}"
                join_room(room)
                emit('joined_room', {'room': room, 'message': 'Joined notification room'})
                print(f"User {user_id} joined notification room")
        except Exception as e:
            emit('error', {'message': f'Failed to join notifications: {str(e)}'})
    
    @socketio.on('leave_notifications')
    def handle_leave_notifications(data):
        """Leave user-specific notification room"""
        try:
            user_id = data.get('user_id')
            if user_id:
                room = f"user_{user_id}"
                leave_room(room)
                emit('left_room', {'room': room, 'message': 'Left notification room'})
        except Exception as e:
            emit('error', {'message': f'Failed to leave notifications: {str(e)}'})


class NotificationBroadcaster:
    """
    Broadcast notifications via WebSocket
    """
    
    def __init__(self):
        self.notification_service = NotificationService()
        self.is_listening = False
        self.listener_thread = None
    
    def start_listening(self):
        """Start listening to Redis pub/sub for notifications"""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.listener_thread = threading.Thread(target=self._listen_for_notifications)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        print("🔊 Started listening for notifications")
    
    def stop_listening(self):
        """Stop listening to notifications"""
        self.is_listening = False
        if self.listener_thread:
            self.listener_thread.join()
    
    def _listen_for_notifications(self):
        """Listen for Redis pub/sub notifications and broadcast via WebSocket"""
        try:
            pubsub = self.notification_service.subscribe_to_notifications()
            
            for message in pubsub.listen():
                if not self.is_listening:
                    break
                
                if message['type'] == 'message':
                    try:
                        notification_data = json.loads(message['data'])
                        self._broadcast_notification(notification_data, message['channel'])
                    except json.JSONDecodeError:
                        print(f"Failed to decode notification: {message['data']}")
                    except Exception as e:
                        print(f"Error processing notification: {str(e)}")
        
        except Exception as e:
            print(f"Error in notification listener: {str(e)}")
    
    def _broadcast_notification(self, notification_data, channel):
        """Broadcast notification to appropriate WebSocket rooms"""
        if not socketio:
            return
        
        try:
            # Extract notification type and user_id
            notification_type = notification_data.get('type', 'system')
            user_id = notification_data.get('user_id')
            
            # Broadcast to general notification room
            socketio.emit('notification', notification_data, room='notifications')
            
            # Broadcast to user-specific room if user_id exists
            if user_id:
                user_room = f"user_{user_id}"
                socketio.emit('notification', notification_data, room=user_room)
            
            # Broadcast to type-specific rooms
            type_room = f"type_{notification_type}"
            socketio.emit('notification', notification_data, room=type_room)
            
            print(f"📡 Broadcasted notification: {notification_type} to user {user_id}")
            
        except Exception as e:
            print(f"Error broadcasting notification: {str(e)}")


# Global broadcaster instance
notification_broadcaster = NotificationBroadcaster()


# REST API routes for notifications
notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/history/<notification_type>', methods=['GET'])
@jwt_required()
def get_notification_history(notification_type):
    """Get notification history for a type"""
    try:
        limit = request.args.get('limit', 20, type=int)
        notification_service = NotificationService()
        history = notification_service.get_notification_history(notification_type, limit)
        
        return {
            'status': 'success',
            'type': notification_type,
            'history': history,
            'count': len(history)
        }
    except Exception as e:
        return {'error': str(e)}, 500

@notifications_bp.route('/test', methods=['POST'])
@jwt_required()
def test_notification():
    """Test notification system"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        message = data.get('message', 'Test notification')
        
        notification_service = NotificationService()
        result = notification_service.send_system_notification(
            message=message,
            level='info',
            data={'test': True}
        )
        
        return {
            'status': 'success' if result else 'failed',
            'message': 'Test notification sent' if result else 'Failed to send notification'
        }
    except Exception as e:
        return {'error': str(e)}, 500