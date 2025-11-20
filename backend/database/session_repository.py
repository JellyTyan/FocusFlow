import aiosqlite
from datetime import datetime
from uuid import uuid4
from typing import Optional
from models.session import Session, SessionStart, SessionStatus, SessionStatusResponse
from config import settings
from exceptions import ValidationError, UnauthorizedAccessError
import logging

logger = logging.getLogger(__name__)

async def start_session(session_data: SessionStart, user_id: str) -> Session:
    """Start new learning session"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify topic ownership
        cursor = await db.execute("""
            SELECT p.user_id FROM topics t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id = ?
        """, (str(session_data.topic_id),))
        row = await cursor.fetchone()
        
        if not row:
            raise ValidationError(f"Topic {session_data.topic_id} not found")
        
        if row[0] != user_id:
            raise UnauthorizedAccessError(f"topic {session_data.topic_id}")
        
        session_id = str(uuid4())
        now = datetime.now().isoformat()
        
        await db.execute("""
            INSERT INTO sessions (id, topic_id, user_id, status, start_time, duration, stuck_moments, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session_id, str(session_data.topic_id), user_id, SessionStatus.ACTIVE.value, now, 0, 0, 0))
        await db.commit()
        
        return await get_session(session_id, user_id)

async def pause_session(session_id: str, user_id: str) -> Session:
    """Pause active session"""
    session = await get_session(session_id, user_id)
    if not session:
        raise ValidationError(f"Session {session_id} not found")
    
    if session.status != SessionStatus.ACTIVE:
        raise ValidationError(f"Session is not active")
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        now = datetime.now().isoformat()
        
        # Calculate duration up to pause
        start_time = datetime.fromisoformat(session.start_time.isoformat())
        pause_time = datetime.now()
        duration = session.duration + int((pause_time - start_time).total_seconds())
        
        await db.execute("""
            UPDATE sessions SET status = ?, pause_time = ?, duration = ?
            WHERE id = ? AND user_id = ?
        """, (SessionStatus.PAUSED.value, now, duration, session_id, user_id))
        await db.commit()
    
    return await get_session(session_id, user_id)

async def resume_session(session_id: str, user_id: str) -> Session:
    """Resume paused session"""
    session = await get_session(session_id, user_id)
    if not session:
        raise ValidationError(f"Session {session_id} not found")
    
    if session.status != SessionStatus.PAUSED:
        raise ValidationError(f"Session is not paused")
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        now = datetime.now().isoformat()
        
        await db.execute("""
            UPDATE sessions SET status = ?, resume_time = ?
            WHERE id = ? AND user_id = ?
        """, (SessionStatus.ACTIVE.value, now, session_id, user_id))
        await db.commit()
    
    return await get_session(session_id, user_id)

async def complete_session(session_id: str, user_id: str) -> Session:
    """Complete session"""
    session = await get_session(session_id, user_id)
    if not session:
        raise ValidationError(f"Session {session_id} not found")
    
    if session.status == SessionStatus.COMPLETED:
        raise ValidationError(f"Session already completed")
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        now = datetime.now().isoformat()
        
        # Calculate final duration
        start_time = datetime.fromisoformat(session.start_time.isoformat())
        end_time = datetime.now()
        duration = session.duration
        
        if session.status == SessionStatus.ACTIVE:
            duration += int((end_time - start_time).total_seconds())
        
        await db.execute("""
            UPDATE sessions SET status = ?, end_time = ?, duration = ?, completed = ?
            WHERE id = ? AND user_id = ?
        """, (SessionStatus.COMPLETED.value, now, duration, 1, session_id, user_id))
        await db.commit()
    
    return await get_session(session_id, user_id)

async def get_session(session_id: str, user_id: str) -> Optional[Session]:
    """Get session by ID"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT * FROM sessions WHERE id = ? AND user_id = ?
        """, (session_id, user_id))
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        return Session(
            id=row[0],
            topic_id=row[1],
            user_id=row[2],
            status=SessionStatus(row[3]),
            start_time=datetime.fromisoformat(row[4]),
            pause_time=datetime.fromisoformat(row[5]) if row[5] else None,
            resume_time=datetime.fromisoformat(row[6]) if row[6] else None,
            end_time=datetime.fromisoformat(row[7]) if row[7] else None,
            duration=row[8],
            stuck_moments=row[9],
            completed=bool(row[10])
        )

async def get_session_status(session_id: str, user_id: str) -> Optional[SessionStatusResponse]:
    """Get session status"""
    session = await get_session(session_id, user_id)
    if not session:
        return None
    
    return SessionStatusResponse(
        id=session.id,
        status=session.status,
        duration=session.duration,
        stuck_moments=session.stuck_moments,
        completed=session.completed
    )