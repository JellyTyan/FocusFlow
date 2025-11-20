import aiosqlite
from datetime import datetime
from uuid import uuid4
from typing import List
from models.chat import ChatMessage, ChatMessageCreate, MessageRole, ChatHistory
from config import settings
from exceptions import ValidationError, UnauthorizedAccessError
import logging

logger = logging.getLogger(__name__)

async def create_message(message_data: ChatMessageCreate, user_id: str, role: MessageRole) -> ChatMessage:
    """Create chat message"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify session ownership
        cursor = await db.execute("""
            SELECT user_id FROM sessions WHERE id = ?
        """, (str(message_data.session_id),))
        row = await cursor.fetchone()
        
        if not row:
            raise ValidationError(f"Session {message_data.session_id} not found")
        
        if row[0] != user_id:
            raise UnauthorizedAccessError(f"session {message_data.session_id}")
        
        message_id = str(uuid4())
        now = datetime.now().isoformat()
        
        await db.execute("""
            INSERT INTO chat_messages (id, session_id, role, content, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (message_id, str(message_data.session_id), role.value, message_data.content, now))
        await db.commit()
        
        return ChatMessage(
            id=message_id,
            session_id=message_data.session_id,
            role=role,
            content=message_data.content,
            timestamp=datetime.fromisoformat(now)
        )

async def get_chat_history(session_id: str, user_id: str) -> ChatHistory:
    """Get chat history for session"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify session ownership
        cursor = await db.execute("""
            SELECT user_id FROM sessions WHERE id = ?
        """, (session_id,))
        row = await cursor.fetchone()
        
        if not row:
            raise ValidationError(f"Session {session_id} not found")
        
        if row[0] != user_id:
            raise UnauthorizedAccessError(f"session {session_id}")
        
        cursor = await db.execute("""
            SELECT * FROM chat_messages WHERE session_id = ? ORDER BY timestamp ASC
        """, (session_id,))
        rows = await cursor.fetchall()
        
        messages = []
        for row in rows:
            message = ChatMessage(
                id=row[0],
                session_id=row[1],
                role=MessageRole(row[2]),
                content=row[3],
                timestamp=datetime.fromisoformat(row[4])
            )
            messages.append(message)
        
        return ChatHistory(session_id=session_id, messages=messages)

async def delete_chat_history(session_id: str, user_id: str) -> bool:
    """Delete chat history for session"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify session ownership
        cursor = await db.execute("""
            SELECT user_id FROM sessions WHERE id = ?
        """, (session_id,))
        row = await cursor.fetchone()
        
        if not row:
            return False
        
        if row[0] != user_id:
            raise UnauthorizedAccessError(f"session {session_id}")
        
        cursor = await db.execute("""
            DELETE FROM chat_messages WHERE session_id = ?
        """, (session_id,))
        await db.commit()
        
        return cursor.rowcount > 0