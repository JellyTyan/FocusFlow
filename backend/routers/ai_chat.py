from fastapi import APIRouter, HTTPException, Depends
from models.chat import ChatMessage, ChatMessageCreate, ChatHistory, MessageRole
from database import chat_repository as db
from database import session_repository, topic_repository, project_repository
from services import ai_service
from dependencies import get_current_user

router = APIRouter()

@router.post("/chat/message", response_model=ChatMessage)
async def send_message(message_data: ChatMessageCreate, current_user: dict = Depends(get_current_user)):
    user_message = await db.create_message(message_data, current_user["id"], MessageRole.USER)
    
    session = await session_repository.get_session(str(message_data.session_id), current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Sesja nie została znaleziona")
    
    topic = await topic_repository.get_topic(str(session.topic_id), current_user["id"])
    if not topic:
        raise HTTPException(status_code=404, detail="Temat nie został znaleziony")
    
    project = await project_repository.get_project(str(topic.project_id), current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie został znaleziony")
    
    history = await db.get_chat_history(str(message_data.session_id), current_user["id"])
    
    ai_response_text = await ai_service.generate_ai_response(
        message_data.content,
        topic.name,
        project.name,
        history.messages
    )
    
    ai_response = await db.create_message(
        ChatMessageCreate(session_id=message_data.session_id, content=ai_response_text),
        current_user["id"],
        MessageRole.ASSISTANT
    )
    
    return ai_response

@router.get("/chat/{session_id}/history", response_model=ChatHistory)
async def get_chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    return await db.get_chat_history(session_id, current_user["id"])

@router.delete("/chat/{session_id}")
async def delete_chat_history(session_id: str, current_user: dict = Depends(get_current_user)):
    success = await db.delete_chat_history(session_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Sesja nie została znaleziona")
    return {"message": "Historia czatu została usunięta"}