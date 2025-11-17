import aiosqlite
from datetime import datetime
from uuid import uuid4
from typing import List, Optional
from models.project import Project, ProjectCreate, ProjectUpdate, Topic

DATABASE_URL = "focusflow.db"

async def init_db():
    """Initialize database tables"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                subject TEXT NOT NULL,
                deadline TEXT NOT NULL,
                created_at TEXT NOT NULL,
                progress REAL DEFAULT 0.0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        await db.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                name TEXT NOT NULL,
                confidence_level INTEGER DEFAULT 1,
                priority_score REAL DEFAULT 0.0,
                stuck_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        """)
        
        await db.commit()

def calculate_priority(confidence_level: int, stuck_count: int, days_to_deadline: int) -> float:
    """Calculate topic priority"""
    if days_to_deadline <= 0:
        days_to_deadline = 1
    
    confidence_factor = 6 - confidence_level
    stuck_multiplier = 1 + (stuck_count * 0.2)
    
    return (1 / days_to_deadline) * confidence_factor * stuck_multiplier

async def create_project(project_data: ProjectCreate, user_id: str) -> Project:
    """Create new project"""
    project_id = str(uuid4())
    now = datetime.now().isoformat()
    
    async with aiosqlite.connect(DATABASE_URL) as db:
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
    return await get_project(project_id)

async def get_all_projects(user_id: str) -> List[Project]:
    """Get all user projects"""
    async with aiosqlite.connect(DATABASE_URL) as db:
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

async def get_project(project_id: str) -> Optional[Project]:
    """Get project by ID"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        project_row = await cursor.fetchone()
        
        if not project_row:
            return None
        
        return await _row_to_project(project_row, db)

async def update_project(project_id: str, update_data: ProjectUpdate) -> Optional[Project]:
    """Update project"""
    update_dict = update_data.dict(exclude_unset=True)
    if not update_dict:
        return await get_project(project_id)
    
    set_clause = ", ".join([f"{key} = ?" for key in update_dict.keys()])
    values = list(update_dict.values())
    values.append(project_id)
    
    async with aiosqlite.connect(DATABASE_URL) as db:
        await db.execute(f"UPDATE projects SET {set_clause} WHERE id = ?", values)
        await db.commit()
    
    await update_priorities(project_id)
    return await get_project(project_id)

async def delete_project(project_id: str) -> bool:
    """Delete project"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Delete topics first
        await db.execute("DELETE FROM topics WHERE project_id = ?", (project_id,))
        
        # Delete project
        cursor = await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        await db.commit()
        
        return cursor.rowcount > 0

async def update_priorities(project_id: str):
    """Update project topic priorities"""
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Get project deadline
        cursor = await db.execute("SELECT deadline FROM projects WHERE id = ?", (project_id,))
        project_row = await cursor.fetchone()
        if not project_row:
            return
        
        deadline = datetime.fromisoformat(project_row[0])
        days_to_deadline = (deadline - datetime.now()).days
        
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
        progress=project_row[6] or 0.0
    )