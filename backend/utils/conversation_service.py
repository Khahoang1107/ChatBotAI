"""
Conversation Memory Service
Manages chat history storage and retrieval for multi-turn conversations
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from utils.database_tools import get_database_tools

class ConversationService:
    """Service for managing conversation memory"""

    def __init__(self):
        self.db_tools = get_database_tools()

    def save_message(self, user_id: int, session_id: str, message_type: str,
                    message_content: str, message_metadata: Optional[Dict[str, Any]] = None) -> int:
        """Save a message to conversation history"""
        conn = self.db_tools.connect()
        if not conn:
            raise Exception("Database connection failed")

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chat_history (user_id, session_id, message_type, message_content, message_metadata)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    user_id,
                    session_id,
                    message_type,
                    message_content,
                    message_metadata or {}
                ))

                message_id = cursor.fetchone()[0]
                conn.commit()
                return message_id

        except Exception as e:
            conn.rollback()
            raise e

    def get_conversation_history(self, user_id: int, session_id: str,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a user session"""
        conn = self.db_tools.connect()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, message_type, message_content, message_metadata, created_at
                    FROM chat_history
                    WHERE user_id = %s AND session_id = %s
                    ORDER BY created_at ASC
                    LIMIT %s
                """, (user_id, session_id, limit))

                messages = []
                for row in cursor.fetchall():
                    messages.append({
                        'id': row[0],
                        'message_type': row[1],
                        'message_content': row[2],
                        'message_metadata': row[3] or {},
                        'created_at': row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4])
                    })

                return messages

        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []

    def get_recent_conversations(self, user_id: int, days: int = 7) -> List[Dict[str, Any]]:
        """Get recent conversation sessions for a user"""
        conn = self.db_tools.connect()
        if not conn:
            return []

        try:
            with conn.cursor() as cursor:
                # Get distinct sessions with their latest message
                cursor.execute("""
                    SELECT DISTINCT session_id,
                           MAX(created_at) as last_message_time,
                           COUNT(*) as message_count
                    FROM chat_history
                    WHERE user_id = %s AND created_at >= %s
                    GROUP BY session_id
                    ORDER BY last_message_time DESC
                """, (user_id, datetime.utcnow() - timedelta(days=days)))

                sessions = []
                for row in cursor.fetchall():
                    sessions.append({
                        'session_id': row[0],
                        'last_message_time': row[1].isoformat() if hasattr(row[1], 'isoformat') else str(row[1]),
                        'message_count': row[2]
                    })

                return sessions

        except Exception as e:
            print(f"Error getting recent conversations: {e}")
            return []

    def delete_old_messages(self, days_to_keep: int = 90) -> int:
        """Delete messages older than specified days"""
        conn = self.db_tools.connect()
        if not conn:
            return 0

        try:
            with conn.cursor() as cursor:
                cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
                cursor.execute("""
                    DELETE FROM chat_history
                    WHERE created_at < %s
                """, (cutoff_date,))

                deleted_count = cursor.rowcount
                conn.commit()
                return deleted_count

        except Exception as e:
            conn.rollback()
            print(f"Error deleting old messages: {e}")
            return 0

    def get_conversation_stats(self, user_id: int) -> Dict[str, Any]:
        """Get conversation statistics for a user"""
        conn = self.db_tools.connect()
        if not conn:
            return {}

        try:
            with conn.cursor() as cursor:
                # Total messages
                cursor.execute("""
                    SELECT COUNT(*) FROM chat_history WHERE user_id = %s
                """, (user_id,))
                total_messages = cursor.fetchone()[0]

                # Messages by type
                cursor.execute("""
                    SELECT message_type, COUNT(*) as count
                    FROM chat_history
                    WHERE user_id = %s
                    GROUP BY message_type
                """, (user_id,))

                message_types = {}
                for row in cursor.fetchall():
                    message_types[row[0]] = row[1]

                # Sessions count
                cursor.execute("""
                    SELECT COUNT(DISTINCT session_id) FROM chat_history WHERE user_id = %s
                """, (user_id,))
                total_sessions = cursor.fetchone()[0]

                return {
                    'total_messages': total_messages,
                    'total_sessions': total_sessions,
                    'message_types': message_types,
                    'avg_messages_per_session': total_messages / max(total_sessions, 1)
                }

        except Exception as e:
            print(f"Error getting conversation stats: {e}")
            return {}

    def format_history_for_groq(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Format conversation history for Groq API"""
        formatted = []

        for msg in messages[-20:]:  # Last 20 messages for context
            role = 'user' if msg['message_type'] == 'user' else 'assistant'
            formatted.append({
                'role': role,
                'content': msg['message_content']
            })

        return formatted

# Global conversation service instance
conversation_service = ConversationService()