from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from sqlalchemy.orm import selectinload
from models.project import Project, ProjectCreate, ProjectUpdate
from models.topic import Topic
from database.models import Project as ProjectModel, Topic as TopicModel
from database.connection import get_db
from services.priority_service import calculate_priority, calculate_days_to_deadline
from exceptions import ProjectNotFoundError, UnauthorizedAccessError, ValidationError
import logging

logger = logging.getLogger(__name__)


async def create_project(project_data: ProjectCreate, user_id: str) -> Project:
    """Tworzy nowy projekt"""
    
    project_id = str(uuid4())
    now = datetime.now()
    
    async for session in get_db():
        project_model = ProjectModel(
            id=project_id,
            user_id=user_id,
            name=project_data.name,
            subject=project_data.subject,
            deadline=project_data.deadline,
            created_at=now
        )
        session.add(project_model)
        
        for topic_name in project_data.topics:
            topic_id = str(uuid4())
            topic_model = TopicModel(
                id=topic_id,
                project_id=project_id,
                name=topic_name,
                created_at=now
            )
            session.add(topic_model)
        
        await session.commit()
        break
    
    await update_priorities(project_id)
    return await get_project(project_id, user_id)


async def get_all_projects(user_id: str) -> List[Project]:
    """Pobiera wszystkie projekty użytkownika"""
    async for session in get_db():
        result = await session.execute(
            select(ProjectModel)
            .where(ProjectModel.user_id == user_id)
            .options(selectinload(ProjectModel.topics))
            .order_by(ProjectModel.created_at.desc())
        )
        project_models = result.scalars().all()
        
        projects = []
        for project_model in project_models:
            projects.append(await _model_to_project(project_model))
        
        return projects


async def get_project(project_id: str, user_id: str = None) -> Optional[Project]:
    """Pobiera projekt po ID z opcjonalną walidacją użytkownika"""
    async for session in get_db():
        query = select(ProjectModel).where(ProjectModel.id == project_id)
        if user_id:
            query = query.where(ProjectModel.user_id == user_id)
        
        query = query.options(selectinload(ProjectModel.topics))
        result = await session.execute(query)
        project_model = result.scalar_one_or_none()
        
        if not project_model:
            return None
        
        if user_id and project_model.user_id != user_id:
            raise UnauthorizedAccessError(f"project {project_id}")
        
        return await _model_to_project(project_model)


async def update_project(project_id: str, update_data: ProjectUpdate, user_id: str) -> Optional[Project]:
    """Aktualizuje projekt z walidacją użytkownika"""
    existing_project = await get_project(project_id, user_id)
    if not existing_project:
        raise ProjectNotFoundError(project_id)
    
    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        return existing_project
    
    
    allowed_fields = {'name', 'subject', 'deadline', 'completed'}
    safe_updates = {k: v for k, v in update_dict.items() if k in allowed_fields}
    
    if not safe_updates:
        return existing_project
    
    async for session in get_db():
        stmt = (
            update(ProjectModel)
            .where(ProjectModel.id == project_id)
            .where(ProjectModel.user_id == user_id)
            .values(**safe_updates)
        )
        await session.execute(stmt)
        await session.commit()
        break
    
    await update_priorities(project_id)
    return await get_project(project_id, user_id)


async def delete_project(project_id: str, user_id: str) -> bool:
    """Usuwa projekt z walidacją użytkownika"""
    existing_project = await get_project(project_id, user_id)
    if not existing_project:
        raise ProjectNotFoundError(project_id)
    
    async for session in get_db():
        await session.execute(
            delete(TopicModel).where(TopicModel.project_id == project_id)
        )
        
        result = await session.execute(
            delete(ProjectModel)
            .where(ProjectModel.id == project_id)
            .where(ProjectModel.user_id == user_id)
        )
        await session.commit()
        
        return result.rowcount > 0


async def update_priorities(project_id: str):
    """Aktualizuje priorytety tematów projektu"""
    async for session in get_db():
        result = await session.execute(
            select(ProjectModel.deadline).where(ProjectModel.id == project_id)
        )
        deadline_row = result.scalar_one_or_none()
        if not deadline_row:
            return
        
        deadline = deadline_row
        days_to_deadline = calculate_days_to_deadline(deadline)
        
        result = await session.execute(
            select(TopicModel)
            .where(TopicModel.project_id == project_id)
        )
        topics = result.scalars().all()
        
        for topic in topics:
            priority = calculate_priority(topic.confidence_level, topic.stuck_count, days_to_deadline)
            topic.priority_score = priority
        
        await session.commit()
        break


async def _model_to_project(project_model: ProjectModel) -> Project:
    """Konwertuje model SQLAlchemy do obiektu Project"""
    topics = []
    for topic_model in project_model.topics:
        topic = Topic(
            id=topic_model.id,
            project_id=topic_model.project_id,
            name=topic_model.name,
            confidence_level=topic_model.confidence_level,
            priority_score=topic_model.priority_score,
            stuck_count=topic_model.stuck_count,
            created_at=topic_model.created_at,
            completed=topic_model.completed
        )
        topics.append(topic)
    
    topics.sort(key=lambda t: t.priority_score, reverse=True)
    
    return Project(
        id=project_model.id,
        name=project_model.name,
        subject=project_model.subject,
        deadline=project_model.deadline,
        created_at=project_model.created_at,
        topics=topics,
        progress=project_model.progress or 0.0,
        completed=project_model.completed or False
    )
