from datetime import datetime
from uuid import uuid4
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.chat import ChatMessage, ChatMessageCreate, MessageRole, ChatHistory
from database.models import ChatMessage as ChatMessageModel, Session as SessionModel
from database.connection import get_db
from exceptions import ValidationError, UnauthorizedAccessError
import logging

logger = logging.getLogger(__name__)

async def create_message(message_data: ChatMessageCreate, user_id: str, role: MessageRole) -> ChatMessage:
    """Create chat message"""
    async for session in get_db():
        # Verify session ownership
        result = await session.execute(
            select(SessionModel.user_id).where(SessionModel.id == str(message_data.session_id))
        )
        session_user_id = result.scalar_one_or_none()
        
        if not session_user_id:
            raise ValidationError(f"Session {message_data.session_id} not found")
        
        if session_user_id != user_id:
            raise UnauthorizedAccessError(f"session {message_data.session_id}")
        
        message_id = str(uuid4())
        now = datetime.now()
        
        message_model = ChatMessageModel(
            id=message_id,
            session_id=str(message_data.session_id),
            role=role.value,
            content=message_data.content,
            timestamp=now
        )
        session.add(message_model)
        await session.commit()
        await session.refresh(message_model)
        
        return ChatMessage(
            id=message_model.id,
            session_id=message_model.session_id,
            role=MessageRole(message_model.role),
            content=message_model.content,
            timestamp=message_model.timestamp
        )


async def get_chat_history(session_id: str, user_id: str) -> ChatHistory:
    """Get chat history for session"""
    async for session in get_db():
        # Verify session ownership
        result = await session.execute(
            select(SessionModel.user_id).where(SessionModel.id == session_id)
        )
        session_user_id = result.scalar_one_or_none()
        
        if not session_user_id:
            raise ValidationError(f"Session {session_id} not found")
        
        if session_user_id != user_id:
            raise UnauthorizedAccessError(f"session {session_id}")
        
        result = await session.execute(
            select(ChatMessageModel)
            .where(ChatMessageModel.session_id == session_id)
            .order_by(ChatMessageModel.timestamp.asc())
        )
        message_models = result.scalars().all()
        
        messages = []
        for message_model in message_models:
            message = ChatMessage(
                id=message_model.id,
                session_id=message_model.session_id,
                role=MessageRole(message_model.role),
                content=message_model.content,
                timestamp=message_model.timestamp
            )
            messages.append(message)
        
        return ChatHistory(session_id=session_id, messages=messages)


async def delete_chat_history(session_id: str, user_id: str) -> bool:
    """Delete chat history for session"""
    async for session in get_db():
        # Verify session ownership
        result = await session.execute(
            select(SessionModel.user_id).where(SessionModel.id == session_id)
        )
        session_user_id = result.scalar_one_or_none()
        
        if not session_user_id:
            return False
        
        if session_user_id != user_id:
            raise UnauthorizedAccessError(f"session {session_id}")
        
        result = await session.execute(
            delete(ChatMessageModel).where(ChatMessageModel.session_id == session_id)
        )
        await session.commit()
        
        return result.rowcount > 0
