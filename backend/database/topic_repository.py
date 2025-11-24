from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload, joinedload
from models.topic import Topic, TopicCreate, TopicUpdate
from database.models import Topic as TopicModel, Project as ProjectModel
from database.connection import get_db
from services.priority_service import calculate_priority, calculate_days_to_deadline
from exceptions import ProjectNotFoundError, UnauthorizedAccessError, ValidationError
import logging

logger = logging.getLogger(__name__)

async def get_project_topics(project_id: str, user_id: str) -> List[Topic]:
    """Get all topics for a project"""
    async for session in get_db():
        # Verify project ownership
        project_result = await session.execute(
            select(ProjectModel.id).where(
                ProjectModel.id == project_id,
                ProjectModel.user_id == user_id
            )
        )
        if not project_result.scalar_one_or_none():
            raise ProjectNotFoundError(project_id)
        
        # Get topics
        result = await session.execute(
            select(TopicModel)
            .where(TopicModel.project_id == project_id)
            .order_by(TopicModel.priority_score.desc())
        )
        topic_models = result.scalars().all()
        
        topics = []
        for topic_model in topic_models:
            topics.append(_model_to_topic(topic_model))
        
        return topics


async def create_topic(project_id: str, topic_data: TopicCreate, user_id: str) -> Topic:
    """Create new topic"""
    async for session in get_db():
        # Verify project ownership
        project_result = await session.execute(
            select(ProjectModel.id).where(
                ProjectModel.id == project_id,
                ProjectModel.user_id == user_id
            )
        )
        if not project_result.scalar_one_or_none():
            raise ProjectNotFoundError(project_id)
        
        topic_id = str(uuid4())
        now = datetime.now()
        
        topic_model = TopicModel(
            id=topic_id,
            project_id=project_id,
            name=topic_data.name,
            confidence_level=topic_data.confidence_level,
            created_at=now
        )
        session.add(topic_model)
        await session.commit()
        await session.refresh(topic_model)
        
        # Calculate initial priority
        await _update_topic_priority(topic_id, session)
        await session.refresh(topic_model)
        
        return _model_to_topic(topic_model)


async def update_topic(topic_id: str, update_data: TopicUpdate, user_id: str) -> Optional[Topic]:
    """Update topic"""
    async for session in get_db():
        # Verify topic ownership through project
        result = await session.execute(
            select(TopicModel, ProjectModel.user_id)
            .join(ProjectModel, TopicModel.project_id == ProjectModel.id)
            .where(TopicModel.id == topic_id)
        )
        row = result.first()
        
        if not row:
            return None
        
        topic_model, project_user_id = row
        
        if project_user_id != user_id:
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return await get_topic(topic_id, user_id)
        
        # Update allowed fields
        if 'name' in update_dict:
            topic_model.name = update_dict['name']
        if 'confidence_level' in update_dict:
            topic_model.confidence_level = update_dict['confidence_level']
        if 'completed' in update_dict:
            topic_model.completed = update_dict['completed']
        
        await session.commit()
        await session.refresh(topic_model)
        
        # Recalculate priority
        await _update_topic_priority(topic_id, session)
        await session.refresh(topic_model)
        
        return await get_topic(topic_id, user_id)


async def delete_topic(topic_id: str, user_id: str) -> bool:
    """Delete topic"""
    async for session in get_db():
        # Verify topic ownership through project
        result = await session.execute(
            select(ProjectModel.user_id)
            .join(TopicModel, TopicModel.project_id == ProjectModel.id)
            .where(TopicModel.id == topic_id)
        )
        project_user_id = result.scalar_one_or_none()
        
        if not project_user_id:
            return False
        
        if project_user_id != user_id:
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        result = await session.execute(
            delete(TopicModel).where(TopicModel.id == topic_id)
        )
        await session.commit()
        
        return result.rowcount > 0


async def get_topic(topic_id: str, user_id: str) -> Optional[Topic]:
    """Get topic by ID"""
    async for session in get_db():
        result = await session.execute(
            select(TopicModel, ProjectModel.user_id)
            .join(ProjectModel, TopicModel.project_id == ProjectModel.id)
            .where(TopicModel.id == topic_id)
        )
        row = result.first()
        
        if not row:
            return None
        
        topic_model, project_user_id = row
        
        if project_user_id != user_id:
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        return _model_to_topic(topic_model)


async def get_topic_priority(topic_id: str, user_id: str) -> float:
    """Get topic priority score"""
    topic = await get_topic(topic_id, user_id)
    if not topic:
        raise ValidationError(f"Topic {topic_id} not found")
    
    return topic.priority_score


async def _update_topic_priority(topic_id: str, session: AsyncSession):
    """Update single topic priority"""
    result = await session.execute(
        select(TopicModel.confidence_level, TopicModel.stuck_count, ProjectModel.deadline)
        .join(ProjectModel, TopicModel.project_id == ProjectModel.id)
        .where(TopicModel.id == topic_id)
    )
    row = result.first()
    
    if row:
        confidence_level, stuck_count, deadline = row
        days_to_deadline = calculate_days_to_deadline(deadline)
        priority = calculate_priority(confidence_level, stuck_count, days_to_deadline)
        
        await session.execute(
            update(TopicModel)
            .where(TopicModel.id == topic_id)
            .values(priority_score=priority)
        )
        await session.commit()


def _model_to_topic(topic_model: TopicModel) -> Topic:
    """Convert SQLAlchemy model to Topic object"""
    return Topic(
        id=topic_model.id,
        project_id=topic_model.project_id,
        name=topic_model.name,
        confidence_level=topic_model.confidence_level,
        priority_score=topic_model.priority_score,
        stuck_count=topic_model.stuck_count,
        created_at=topic_model.created_at,
        completed=topic_model.completed or False
    )
