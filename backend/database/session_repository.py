from datetime import datetime
from uuid import uuid4
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.session import Session, SessionStart, SessionStatus, SessionStatusResponse
from database.models import Session as SessionModel, Topic as TopicModel, Project as ProjectModel
from database.connection import get_db
from exceptions import ValidationError, UnauthorizedAccessError
import logging

logger = logging.getLogger(__name__)

async def start_session(session_data: SessionStart, user_id: str) -> Session:
    """Start new learning session"""
    async for session in get_db():
        # Verify topic ownership
        result = await session.execute(
            select(ProjectModel.user_id)
            .join(TopicModel, TopicModel.project_id == ProjectModel.id)
            .where(TopicModel.id == str(session_data.topic_id))
        )
        project_user_id = result.scalar_one_or_none()
        
        if not project_user_id:
            raise ValidationError(f"Topic {session_data.topic_id} not found")
        
        if project_user_id != user_id:
            raise UnauthorizedAccessError(f"topic {session_data.topic_id}")
        
        session_id = str(uuid4())
        now = datetime.now()
        
        session_model = SessionModel(
            id=session_id,
            topic_id=str(session_data.topic_id),
            user_id=user_id,
            status=SessionStatus.ACTIVE.value,
            start_time=now,
            duration=0,
            stuck_moments=0,
            completed=False
        )
        session.add(session_model)
        await session.commit()
        await session.refresh(session_model)
        
        return await get_session(session_id, user_id)


async def pause_session(session_id: str, user_id: str) -> Session:
    """Pause active session"""
    session_obj = await get_session(session_id, user_id)
    if not session_obj:
        raise ValidationError(f"Session {session_id} not found")
    
    if session_obj.status != SessionStatus.ACTIVE:
        raise ValidationError(f"Session is not active")
    
    async for session in get_db():
        result = await session.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id
            )
        )
        session_model = result.scalar_one_or_none()
        if not session_model:
            raise ValidationError(f"Session {session_id} not found")
        
        now = datetime.now()
        
        # Calculate duration up to pause
        start_time = session_model.start_time
        pause_time = now
        duration = session_model.duration + int((pause_time - start_time).total_seconds())
        
        session_model.status = SessionStatus.PAUSED.value
        session_model.pause_time = now
        session_model.duration = duration
        
        await session.commit()
        await session.refresh(session_model)
        break
    
    return await get_session(session_id, user_id)


async def resume_session(session_id: str, user_id: str) -> Session:
    """Resume paused session"""
    session_obj = await get_session(session_id, user_id)
    if not session_obj:
        raise ValidationError(f"Session {session_id} not found")
    
    if session_obj.status != SessionStatus.PAUSED:
        raise ValidationError(f"Session is not paused")
    
    async for session in get_db():
        result = await session.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id
            )
        )
        session_model = result.scalar_one_or_none()
        if not session_model:
            raise ValidationError(f"Session {session_id} not found")
        
        now = datetime.now()
        
        session_model.status = SessionStatus.ACTIVE.value
        session_model.resume_time = now
        
        await session.commit()
        await session.refresh(session_model)
        break
    
    return await get_session(session_id, user_id)


async def complete_session(session_id: str, user_id: str) -> Session:
    """Complete session"""
    session_obj = await get_session(session_id, user_id)
    if not session_obj:
        raise ValidationError(f"Session {session_id} not found")
    
    if session_obj.status == SessionStatus.COMPLETED:
        raise ValidationError(f"Session already completed")
    
    async for session in get_db():
        result = await session.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id
            )
        )
        session_model = result.scalar_one_or_none()
        if not session_model:
            raise ValidationError(f"Session {session_id} not found")
        
        now = datetime.now()
        
        # Calculate final duration
        start_time = session_model.start_time
        end_time = now
        duration = session_model.duration
        
        if session_model.status == SessionStatus.ACTIVE.value:
            duration += int((end_time - start_time).total_seconds())
        
        session_model.status = SessionStatus.COMPLETED.value
        session_model.end_time = now
        session_model.duration = duration
        session_model.completed = True
        
        await session.commit()
        await session.refresh(session_model)
        break
    
    return await get_session(session_id, user_id)


async def get_session(session_id: str, user_id: str) -> Optional[Session]:
    """Get session by ID"""
    async for session in get_db():
        result = await session.execute(
            select(SessionModel).where(
                SessionModel.id == session_id,
                SessionModel.user_id == user_id
            )
        )
        session_model = result.scalar_one_or_none()
        
        if not session_model:
            return None
        
        return _model_to_session(session_model)


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


def _model_to_session(session_model: SessionModel) -> Session:
    """Convert SQLAlchemy model to Session object"""
    return Session(
        id=session_model.id,
        topic_id=session_model.topic_id,
        user_id=session_model.user_id,
        status=SessionStatus(session_model.status),
        start_time=session_model.start_time,
        pause_time=session_model.pause_time,
        resume_time=session_model.resume_time,
        end_time=session_model.end_time,
        duration=session_model.duration,
        stuck_moments=session_model.stuck_moments,
        completed=session_model.completed or False
    )
