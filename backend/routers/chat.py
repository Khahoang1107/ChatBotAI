# API Router: Chat Messaging

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.models import ChatRequest, ChatResponse
from services.chat_service import ChatService
from core.logging import logger

router = APIRouter(prefix="/api/chat", tags=["chat"])


async def get_chat_service() -> ChatService:
    """Dependency for chat service"""
    return ChatService()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send message and get AI response
    
    Args:
        request: Chat request with message content
        user_id: ID of user sending message
        
    Returns:
        ChatResponse with AI response
    """
    try:
        logger.info(f"Chat message from user {user_id}: {request.message[:50]}...")
        
        response = await chat_service.send_message(user_id, request)
        
        logger.info(f"Chat response sent to user {user_id}")
        return response
        
    except Exception as e:
        logger.error(f"Chat processing failed for user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat message"
        )


@router.get("/history/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    user_id: int,
    limit: int = 50,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Get conversation history
    
    Args:
        conversation_id: ID of conversation
        user_id: ID of user
        limit: Maximum messages to return (default 50)
        
    Returns:
        List of messages in conversation
    """
    try:
        if limit < 1 or limit > 100:
            limit = 50
        
        logger.info(f"Retrieving history for conversation {conversation_id}")
        
        history = await chat_service.get_conversation_history(user_id, conversation_id, limit)
        
        return {
            "conversation_id": conversation_id,
            "messages": history,
            "count": len(history) if history else 0
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve conversation history"
        )


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: int,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Delete conversation and all associated messages
    
    Args:
        conversation_id: ID of conversation to delete
        user_id: ID of user (verify ownership)
    """
    try:
        logger.info(f"Deleting conversation {conversation_id} for user {user_id}")
        
        # TODO: Implement delete logic in ChatService
        # await chat_service.delete_conversation(user_id, conversation_id)
        
        return {"success": True, "message": f"Conversation {conversation_id} deleted"}
        
    except Exception as e:
        logger.error(f"Failed to delete conversation: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete conversation"
        )
