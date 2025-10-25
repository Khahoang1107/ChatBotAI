"""
WebSocket Manager for Real-time OCR Notifications
"""

from typing import Dict, List
from fastapi import WebSocket
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manage WebSocket connections for real-time notifications"""

    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """Connect a WebSocket client"""
        await websocket.accept()

        if user_id not in self.active_connections:
            self.active_connections[user_id] = []

        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: {user_id} (total: {len(self.active_connections[user_id])})")

        # Send welcome message
        await self.send_to_client(websocket, {
            "type": "connected",
            "message": "Connected to OCR notification service",
            "timestamp": datetime.now().isoformat()
        })

    def disconnect(self, websocket: WebSocket, user_id: str = "anonymous"):
        """Disconnect a WebSocket client"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
                logger.info(f"WebSocket disconnected: {user_id} (remaining: {len(self.active_connections[user_id])})")

                # Clean up empty user lists
                if not self.active_connections[user_id]:
                    del self.active_connections[user_id]

    async def send_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a specific user"""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to {user_id}: {e}")
                    disconnected.append(websocket)

            # Remove disconnected clients
            for websocket in disconnected:
                self.disconnect(websocket, user_id)

    async def send_to_client(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send to client: {e}")

    async def broadcast(self, message: dict):
        """Send message to all connected clients"""
        for user_id, connections in self.active_connections.items():
            await self.send_to_user(user_id, message)

    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return sum(len(connections) for connections in self.active_connections.values())

    def get_user_count(self) -> int:
        """Get number of unique users connected"""
        return len(self.active_connections)

# Global WebSocket manager instance
websocket_manager = WebSocketManager()