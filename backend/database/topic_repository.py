import aiosqlite
from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from models.topic import Topic, TopicCreate, TopicUpdate
from config import settings
from services.priority_service import calculate_priority, calculate_days_to_deadline
from exceptions import ProjectNotFoundError, UnauthorizedAccessError, ValidationError
import logging

logger = logging.getLogger(__name__)

async def get_project_topics(project_id: str, user_id: str) -> List[Topic]:
    """Get all topics for a project"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify project ownership
        cursor = await db.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        if not await cursor.fetchone():
            raise ProjectNotFoundError(project_id)
        
        cursor = await db.execute(
            "SELECT * FROM topics WHERE project_id = ? ORDER BY priority_score DESC",
            (project_id,)
        )
        topic_rows = await cursor.fetchall()
        
        topics = []
        for row in topic_rows:
            topic = Topic(
                id=row[0],
                project_id=row[1],
                name=row[2],
                confidence_level=row[3],
                priority_score=row[4],
                stuck_count=row[5],
                created_at=datetime.fromisoformat(row[6])
            )
            topics.append(topic)
        
        return topics

async def create_topic(project_id: str, topic_data: TopicCreate, user_id: str) -> Topic:
    """Create new topic"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify project ownership
        cursor = await db.execute("SELECT id FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        if not await cursor.fetchone():
            raise ProjectNotFoundError(project_id)
        
        topic_id = str(uuid4())
        now = datetime.now().isoformat()
        
        await db.execute(
            "INSERT INTO topics (id, project_id, name, confidence_level, created_at) VALUES (?, ?, ?, ?, ?)",
            (topic_id, project_id, topic_data.name, topic_data.confidence_level, now)
        )
        await db.commit()
        
        # Calculate initial priority
        await _update_topic_priority(topic_id, db)
        
        # Get created topic
        cursor = await db.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
        row = await cursor.fetchone()
        
        return Topic(
            id=row[0],
            project_id=row[1],
            name=row[2],
            confidence_level=row[3],
            priority_score=row[4],
            stuck_count=row[5],
            created_at=datetime.fromisoformat(row[6])
        )

async def update_topic(topic_id: str, update_data: TopicUpdate, user_id: str) -> Optional[Topic]:
    """Update topic"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify topic ownership through project
        cursor = await db.execute("""
            SELECT t.*, p.user_id FROM topics t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id = ?
        """, (topic_id,))
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        if row[7] != user_id:  # user_id is at index 7
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        update_dict = update_data.dict(exclude_unset=True)
        if not update_dict:
            return await get_topic(topic_id, user_id)
        
        # Update allowed fields
        if 'confidence_level' in update_dict:
            await db.execute(
                "UPDATE topics SET confidence_level = ? WHERE id = ?",
                (update_dict['confidence_level'], topic_id)
            )
        
        await db.commit()
        
        # Recalculate priority
        await _update_topic_priority(topic_id, db)
        
        return await get_topic(topic_id, user_id)

async def delete_topic(topic_id: str, user_id: str) -> bool:
    """Delete topic"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify topic ownership through project
        cursor = await db.execute("""
            SELECT p.user_id FROM topics t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id = ?
        """, (topic_id,))
        row = await cursor.fetchone()
        
        if not row:
            return False
        
        if row[0] != user_id:
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        cursor = await db.execute("DELETE FROM topics WHERE id = ?", (topic_id,))
        await db.commit()
        
        return cursor.rowcount > 0

async def get_topic(topic_id: str, user_id: str) -> Optional[Topic]:
    """Get topic by ID"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT t.*, p.user_id FROM topics t 
            JOIN projects p ON t.project_id = p.id 
            WHERE t.id = ?
        """, (topic_id,))
        row = await cursor.fetchone()
        
        if not row:
            return None
        
        if row[7] != user_id:
            raise UnauthorizedAccessError(f"topic {topic_id}")
        
        return Topic(
            id=row[0],
            project_id=row[1],
            name=row[2],
            confidence_level=row[3],
            priority_score=row[4],
            stuck_count=row[5],
            created_at=datetime.fromisoformat(row[6])
        )

async def get_topic_priority(topic_id: str, user_id: str) -> float:
    """Get topic priority score"""
    topic = await get_topic(topic_id, user_id)
    if not topic:
        raise ValidationError(f"Topic {topic_id} not found")
    
    return topic.priority_score

async def _update_topic_priority(topic_id: str, db):
    """Update single topic priority"""
    cursor = await db.execute("""
        SELECT t.confidence_level, t.stuck_count, p.deadline 
        FROM topics t 
        JOIN projects p ON t.project_id = p.id 
        WHERE t.id = ?
    """, (topic_id,))
    row = await cursor.fetchone()
    
    if row:
        confidence_level, stuck_count, deadline_str = row
        deadline = datetime.fromisoformat(deadline_str)
        days_to_deadline = calculate_days_to_deadline(deadline)
        priority = calculate_priority(confidence_level, stuck_count, days_to_deadline)
        
        await db.execute(
            "UPDATE topics SET priority_score = ? WHERE id = ?",
            (priority, topic_id)
        )
        await db.commit()