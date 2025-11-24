from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from models.stats import StatsOverview, ProjectStats, StuckTopic, StuckTopics
from database.models import Session as SessionModel, Project as ProjectModel, Topic as TopicModel
from database.connection import get_db
import logging

logger = logging.getLogger(__name__)

async def get_overview_stats(user_id: str) -> StatsOverview:
    """Get overall statistics for user"""
    async for session in get_db():
        # Total sessions
        result = await session.execute(
            select(func.count(SessionModel.id)).where(SessionModel.user_id == user_id)
        )
        total_sessions = result.scalar() or 0
        
        # Completed sessions
        result = await session.execute(
            select(func.count(SessionModel.id)).where(
                SessionModel.user_id == user_id,
                SessionModel.completed == True
            )
        )
        completed_sessions = result.scalar() or 0
        
        # Total study time
        result = await session.execute(
            select(func.sum(SessionModel.duration)).where(SessionModel.user_id == user_id)
        )
        total_study_time = result.scalar() or 0
        
        # Total projects
        result = await session.execute(
            select(func.count(ProjectModel.id)).where(ProjectModel.user_id == user_id)
        )
        total_projects = result.scalar() or 0
        
        # Total topics
        result = await session.execute(
            select(func.count(TopicModel.id))
            .join(ProjectModel, TopicModel.project_id == ProjectModel.id)
            .where(ProjectModel.user_id == user_id)
        )
        total_topics = result.scalar() or 0
        
        return StatsOverview(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            total_study_time=total_study_time,
            total_projects=total_projects,
            total_topics=total_topics
        )


async def get_project_stats(project_id: str, user_id: str) -> ProjectStats:
    """Get statistics for specific project"""
    async for session in get_db():
        # Verify ownership
        result = await session.execute(
            select(ProjectModel.id).where(
                ProjectModel.id == project_id,
                ProjectModel.user_id == user_id
            )
        )
        if not result.scalar_one_or_none():
            return None
        
        # Total sessions for project topics
        result = await session.execute(
            select(func.count(SessionModel.id))
            .join(TopicModel, SessionModel.topic_id == TopicModel.id)
            .where(
                TopicModel.project_id == project_id,
                SessionModel.user_id == user_id
            )
        )
        total_sessions = result.scalar() or 0
        
        # Completed sessions
        result = await session.execute(
            select(func.count(SessionModel.id))
            .join(TopicModel, SessionModel.topic_id == TopicModel.id)
            .where(
                TopicModel.project_id == project_id,
                SessionModel.user_id == user_id,
                SessionModel.completed == True
            )
        )
        completed_sessions = result.scalar() or 0
        
        # Total study time
        result = await session.execute(
            select(func.sum(SessionModel.duration))
            .join(TopicModel, SessionModel.topic_id == TopicModel.id)
            .where(
                TopicModel.project_id == project_id,
                SessionModel.user_id == user_id
            )
        )
        total_study_time = result.scalar() or 0
        
        # Topics count
        result = await session.execute(
            select(func.count(TopicModel.id)).where(TopicModel.project_id == project_id)
        )
        topics_count = result.scalar() or 0
        
        # Average confidence
        result = await session.execute(
            select(func.avg(TopicModel.confidence_level)).where(TopicModel.project_id == project_id)
        )
        average_confidence = result.scalar() or 0.0
        
        return ProjectStats(
            project_id=project_id,
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            total_study_time=total_study_time,
            topics_count=topics_count,
            average_confidence=float(average_confidence)
        )


async def get_stuck_topics(user_id: str, limit: int = 10) -> StuckTopics:
    """Get topics where user gets stuck most often"""
    async for session in get_db():
        result = await session.execute(
            select(
                TopicModel.id,
                TopicModel.name,
                ProjectModel.name,
                TopicModel.stuck_count,
                TopicModel.confidence_level
            )
            .join(ProjectModel, TopicModel.project_id == ProjectModel.id)
            .where(
                ProjectModel.user_id == user_id,
                TopicModel.stuck_count > 0
            )
            .order_by(TopicModel.stuck_count.desc())
            .limit(limit)
        )
        rows = result.all()
        
        topics = []
        for row in rows:
            topic = StuckTopic(
                topic_id=row[0],
                topic_name=row[1],
                project_name=row[2],
                stuck_count=row[3],
                confidence_level=row[4]
            )
            topics.append(topic)
        
        return StuckTopics(topics=topics)
