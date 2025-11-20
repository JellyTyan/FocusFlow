from fastapi import APIRouter, HTTPException, Depends
from models.chat import ChatMessage, ChatMessageCreate, ChatHistory, MessageRole
from database import chat_repository as db
from database import session_repository, topic_repository, project_repository
from services import ai_service
from dependencies import get_current_user

router = APIRouter()

@router.post("/chat/message", response_model=ChatMessage)
async def send_message(message_data: ChatMessageCreate, current_user: dict = Depends(get_current_user)):
    """Send message to AI and get response"""
    # Save user message
    user_message = await db.create_message(message_data, current_user["id"], MessageRole.USER)
    
    # Get session context
    session = await session_repository.get_session(str(message_data.session_id), current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get topic and project info
    topic = await topic_repository.get_topic(str(session.topic_id), current_user["id"])
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    project = await project_repository.get_project(str(topic.project_id), current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get chat history
    history = await db.get_chat_history(str(message_data.session_id), current_user["id"])
    
    # Generate AI response
    ai_response_text = await ai_service.generate_ai_response(
        message_data.content,
        topic.name,
        project.name,
        history.messages
    )
    
    # Save AI response
    ai_response = await db.create_message(
        ChatMessageCreate(session_id=message_data.session_id, content=ai_response_text),
        current_user["id"],
        MessageRole.ASSISTANT
    )
    
    return ai_response

@router.get("/chat/{session_id}/history", response_model=ChatHistory)
async def get_chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get chat history for session"""
    return await db.get_chat_history(session_id, current_user["id"])

@router.delete("/chat/{session_id}")
async def delete_chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    """Delete chat history"""
    success = await db.delete_chat_history(session_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Chat history deleted"}