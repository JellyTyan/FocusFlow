from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from models.subject import Subject, SubjectCreate
from database.models import Subject as SubjectModel
from database.connection import get_db
import logging

logger = logging.getLogger(__name__)

async def create_subject(subject_data: SubjectCreate, user_id: str) -> Subject:
    """Create new subject"""
    async for session in get_db():
        # Check if subject with this name already exists for user
        result = await session.execute(
            select(SubjectModel.id).where(
                SubjectModel.user_id == user_id,
                func.lower(SubjectModel.name) == func.lower(subject_data.name)
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            # Return existing subject
            return await get_subject(existing, user_id)
        
        subject_id = str(uuid4())
        now = datetime.now()
        
        subject_model = SubjectModel(
            id=subject_id,
            user_id=user_id,
            name=subject_data.name,
            created_at=now
        )
        session.add(subject_model)
        await session.commit()
        await session.refresh(subject_model)
        
        return await get_subject(subject_id, user_id)


async def get_all_subjects(user_id: str) -> List[Subject]:
    """Get all user subjects"""
    async for session in get_db():
        result = await session.execute(
            select(SubjectModel)
            .where(SubjectModel.user_id == user_id)
            .order_by(SubjectModel.name.asc())
        )
        subject_models = result.scalars().all()
        
        subjects = []
        for subject_model in subject_models:
            subjects.append(Subject(
                id=subject_model.id,
                user_id=subject_model.user_id,
                name=subject_model.name,
                created_at=subject_model.created_at
            ))
        
        return subjects


async def get_subject(subject_id: str, user_id: str) -> Optional[Subject]:
    """Get subject by ID"""
    async for session in get_db():
        result = await session.execute(
            select(SubjectModel).where(
                SubjectModel.id == subject_id,
                SubjectModel.user_id == user_id
            )
        )
        subject_model = result.scalar_one_or_none()
        
        if not subject_model:
            return None
        
        return Subject(
            id=subject_model.id,
            user_id=subject_model.user_id,
            name=subject_model.name,
            created_at=subject_model.created_at
        )


async def delete_subject(subject_id: str, user_id: str) -> bool:
    """Delete subject"""
    async for session in get_db():
        result = await session.execute(
            delete(SubjectModel).where(
                SubjectModel.id == subject_id,
                SubjectModel.user_id == user_id
            )
        )
        await session.commit()
        return result.rowcount > 0
