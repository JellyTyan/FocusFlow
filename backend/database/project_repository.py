import aiosqlite
from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from models.project import Project, ProjectCreate, ProjectUpdate
from models.topic import Topic
from config import settings
from services.priority_service import calculate_priority, calculate_days_to_deadline
from exceptions import ProjectNotFoundError, UnauthorizedAccessError, ValidationError
import logging

logger = logging.getLogger(__name__)



async def create_project(project_data: ProjectCreate, user_id: str) -> Project:
    """Create new project"""
    # Validate deadline
    if project_data.deadline <= datetime.now():
        raise ValidationError("Deadline must be in the future")
    
    project_id = str(uuid4())
    now = datetime.now().isoformat()
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        await db.execute(
            "INSERT INTO projects (id, user_id, name, subject, deadline, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, user_id, project_data.name, project_data.subject, project_data.deadline.isoformat(), now)
        )
        
        # Create topics
        for topic_name in project_data.topics:
            topic_id = str(uuid4())
            await db.execute(
                "INSERT INTO topics (id, project_id, name, created_at) VALUES (?, ?, ?, ?)",
                (topic_id, project_id, topic_name, now)
            )
        
        await db.commit()
    
    # Update priorities
    await update_priorities(project_id)
    
    # Get the created project
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project_row = await cursor.fetchone()
        return await _row_to_project(project_row, db)

async def get_all_projects(user_id: str) -> List[Project]:
    """Get all user projects"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT * FROM projects WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        projects = await cursor.fetchall()
        
        result = []
        for project_row in projects:
            project = await _row_to_project(project_row, db)
            result.append(project)
        
        return result

async def get_project(project_id: str, user_id: str = None) -> Optional[Project]:
    """Get project by ID with optional user validation"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        if user_id:
            cursor = await db.execute("SELECT * FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        else:
            cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        
        project_row = await cursor.fetchone()
        
        if not project_row:
            return None
        
        if user_id and project_row[1] != user_id:
            raise UnauthorizedAccessError(f"project {project_id}")
        
        return await _row_to_project(project_row, db)

async def update_project(project_id: str, update_data: ProjectUpdate, user_id: str) -> Optional[Project]:
    """Update project with user validation"""
    # Validate ownership first
    existing_project = await get_project(project_id, user_id)
    if not existing_project:
        raise ProjectNotFoundError(project_id)
    
    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        return existing_project
    
    # Validate deadline if being updated
    if 'deadline' in update_dict and update_dict['deadline'] <= datetime.now():
        raise ValidationError("Deadline must be in the future")
    
    # Safe SQL update with allowed fields only
    allowed_fields = {'name', 'subject', 'deadline'}
    safe_updates = {k: v for k, v in update_dict.items() if k in allowed_fields}
    
    if not safe_updates:
        return existing_project
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        for field, value in safe_updates.items():
            if field == 'deadline':
                value = value.isoformat()
            await db.execute(f"UPDATE projects SET {field} = ? WHERE id = ? AND user_id = ?", (value, project_id, user_id))
        await db.commit()
    
    await update_priorities(project_id)
    return await get_project(project_id, user_id)

async def delete_project(project_id: str, user_id: str) -> bool:
    """Delete project with user validation"""
    # Validate ownership first
    existing_project = await get_project(project_id, user_id)
    if not existing_project:
        raise ProjectNotFoundError(project_id)
    
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Delete topics first
        await db.execute("DELETE FROM topics WHERE project_id = ?", (project_id,))
        
        # Delete project
        cursor = await db.execute("DELETE FROM projects WHERE id = ? AND user_id = ?", (project_id, user_id))
        await db.commit()
        
        return cursor.rowcount > 0

async def update_priorities(project_id: str):
    """Update project topic priorities"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Get project deadline
        cursor = await db.execute("SELECT deadline FROM projects WHERE id = ?", (project_id,))
        project_row = await cursor.fetchone()
        if not project_row:
            return
        
        deadline = datetime.fromisoformat(project_row[0])
        days_to_deadline = calculate_days_to_deadline(deadline)
        
        # Update topic priorities
        cursor = await db.execute(
            "SELECT id, confidence_level, stuck_count FROM topics WHERE project_id = ?",
            (project_id,)
        )
        topics = await cursor.fetchall()
        
        for topic_id, confidence_level, stuck_count in topics:
            priority = calculate_priority(confidence_level, stuck_count, days_to_deadline)
            await db.execute(
                "UPDATE topics SET priority_score = ? WHERE id = ?",
                (priority, topic_id)
            )
        
        await db.commit()

async def _row_to_project(project_row, db) -> Project:
    """Convert database row to Project object"""
    project_id = project_row[0]
    
    # Get topics
    cursor = await db.execute(
        "SELECT * FROM topics WHERE project_id = ? ORDER BY priority_score DESC",
        (project_id,)
    )
    topic_rows = await cursor.fetchall()
    
    topics = []
    for topic_row in topic_rows:
        topic = Topic(
            id=topic_row[0],
            project_id=topic_row[1],
            name=topic_row[2],
            confidence_level=topic_row[3],
            priority_score=topic_row[4],
            stuck_count=topic_row[5],
            created_at=datetime.fromisoformat(topic_row[6])
        )
        topics.append(topic)
    
    return Project(
        id=project_row[0],
        name=project_row[2],
        subject=project_row[3],
        deadline=datetime.fromisoformat(project_row[4]),
        created_at=datetime.fromisoformat(project_row[5]),
        topics=topics,
        progress=project_row[6] if len(project_row) > 6 and project_row[6] is not None else 0.0
    )