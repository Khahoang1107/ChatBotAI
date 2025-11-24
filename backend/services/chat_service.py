# Service Layer: Chat Management

from typing import List, Optional
from datetime import datetime
from core.exceptions import (
    AuthenticationException,
    ExternalServiceException,
    DatabaseException,
    ValidationException
)
from core.dependencies import container
from schemas.models import ChatRequest, ChatResponse


class ChatService:
    """Chat message handling and Groq AI integration"""
    
    def __init__(self):
        self.db = container.db
        self.groq_client = container.groq_client
        self.settings = container.settings
    
    async def send_message(self, user_id: int, request: ChatRequest) -> ChatResponse:
        """
        Send user message and get AI response from Groq
        
        Args:
            user_id: ID of user sending message
            request: ChatRequest with message content
            
        Returns:
            ChatResponse with AI response
            
        Raises:
            ValidationException: If message is empty or too long
            ExternalServiceException: If Groq API fails
            DatabaseException: If database operation fails
        """
        try:
            # Validate message
            if not request.message or len(request.message.strip()) == 0:
                raise ValidationException("Message cannot be empty")
            
            if len(request.message) > 2000:
                raise ValidationException("Message too long (max 2000 characters)")
            
            # Get conversation context
            conversation_id = request.conversation_id or str(user_id)
            
            # Fetch recent messages for context (last 5)
            context_messages = self._get_conversation_context(user_id, conversation_id)
            
            # Call Groq API
            groq_response = await self._call_groq(request.message, context_messages)
            
            # Store messages in database
            self._store_messages(
                user_id=user_id,
                user_message=request.message,
                ai_response=groq_response["content"],
                conversation_id=conversation_id
            )
            
            return ChatResponse(
                response=groq_response["content"],
                conversation_id=conversation_id,
                tokens_used=groq_response.get("tokens", 0)
            )
            
        except (ValidationException, ExternalServiceException):
            raise
        except Exception as e:
            raise DatabaseException(f"Chat processing failed: {str(e)}")
    
    async def _call_groq(self, message: str, context: List[dict]) -> dict:
        """
        Call Groq API with message and context
        
        Args:
            message: User message
            context: Previous messages for context
            
        Returns:
            Dict with content and tokens
        """
        try:
            # Prepare messages for Groq
            messages = context + [{"role": "user", "content": message}]
            
            # Call Groq (using groq_tools or direct API)
            # response = await self.groq_client.chat.completions.create(
            #     model="mixtral-8x7b-32768",
            #     messages=messages,
            #     max_tokens=1024,
            #     temperature=0.7
            # )
            
            # Placeholder for actual Groq call
            return {
                "content": f"AI response to: {message}",
                "tokens": 100
            }
            
        except Exception as e:
            raise ExternalServiceException(f"Groq API call failed: {str(e)}")
    
    def _get_conversation_context(self, user_id: int, conversation_id: str) -> List[dict]:
        """Fetch recent messages from conversation"""
        try:
            # Query messages from database
            # messages = self.db.query(Message).filter(
            #     Message.user_id == user_id,
            #     Message.conversation_id == conversation_id
            # ).order_by(Message.created_at.desc()).limit(5).all()
            
            # Placeholder
            return []
        except Exception as e:
            raise DatabaseException(f"Failed to get conversation context: {str(e)}")
    
    def _store_messages(self, user_id: int, user_message: str, ai_response: str, conversation_id: str):
        """Store user and AI messages in database"""
        try:
            # message1 = Message(
            #     user_id=user_id,
            #     sender="user",
            #     content=user_message,
            #     conversation_id=conversation_id,
            #     created_at=datetime.utcnow()
            # )
            # message2 = Message(
            #     user_id=user_id,
            #     sender="ai",
            #     content=ai_response,
            #     conversation_id=conversation_id,
            #     created_at=datetime.utcnow()
            # )
            # self.db.add(message1)
            # self.db.add(message2)
            # self.db.commit()
            pass
        except Exception as e:
            self.db.rollback()
            raise DatabaseException(f"Failed to store messages: {str(e)}")
    
    async def get_conversation_history(self, user_id: int, conversation_id: str, limit: int = 50):
        """Retrieve conversation history"""
        try:
            # messages = self.db.query(Message).filter(
            #     Message.user_id == user_id,
            #     Message.conversation_id == conversation_id
            # ).order_by(Message.created_at.asc()).limit(limit).all()
            
            # return [MessageResponse.from_orm(m) for m in messages]
            return []
        except Exception as e:
            raise DatabaseException(f"Failed to retrieve conversation: {str(e)}")
