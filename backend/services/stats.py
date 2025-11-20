import aiosqlite
from typing import List
from models.stats import StatsOverview, ProjectStats, StuckTopic, StuckTopics
from config import settings
import logging

logger = logging.getLogger(__name__)

async def get_overview_stats(user_id: str) -> StatsOverview:
    """Get overall statistics for user"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Total sessions
        cursor = await db.execute("""
            SELECT COUNT(*) FROM sessions WHERE user_id = ?
        """, (user_id,))
        total_sessions = (await cursor.fetchone())[0]
        
        # Completed sessions
        cursor = await db.execute("""
            SELECT COUNT(*) FROM sessions WHERE user_id = ? AND completed = 1
        """, (user_id,))
        completed_sessions = (await cursor.fetchone())[0]
        
        # Total study time
        cursor = await db.execute("""
            SELECT SUM(duration) FROM sessions WHERE user_id = ?
        """, (user_id,))
        total_study_time = (await cursor.fetchone())[0] or 0
        
        # Total projects
        cursor = await db.execute("""
            SELECT COUNT(*) FROM projects WHERE user_id = ?
        """, (user_id,))
        total_projects = (await cursor.fetchone())[0]
        
        # Total topics
        cursor = await db.execute("""
            SELECT COUNT(*) FROM topics t
            JOIN projects p ON t.project_id = p.id
            WHERE p.user_id = ?
        """, (user_id,))
        total_topics = (await cursor.fetchone())[0]
        
        return StatsOverview(
            total_sessions=total_sessions,
            completed_sessions=completed_sessions,
            total_study_time=total_study_time,
            total_projects=total_projects,
            total_topics=total_topics
        )

async def get_project_stats(project_id: str, user_id: str) -> ProjectStats:
    """Get statistics for specific project"""
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        # Verify ownership
        cursor = await db.execute("""
            SELECT id FROM projects WHERE id = ? AND user_id = ?
        """, (project_id, user_id))
        if not await cursor.fetchone():
            return None
        
        # Total sessions for project topics
        cursor = await db.execute("""
            SELECT COUNT(*) FROM sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE t.project_id = ? AND s.user_id = ?
        """, (project_id, user_id))
        total_sessions = (await cursor.fetchone())[0]
        
        # Completed sessions
        cursor = await db.execute("""
            SELECT COUNT(*) FROM sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE t.project_id = ? AND s.user_id = ? AND s.completed = 1
        """, (project_id, user_id))
        completed_sessions = (await cursor.fetchone())[0]
        
        # Total study time
        cursor = await db.execute("""
            SELECT SUM(s.duration) FROM sessions s
            JOIN topics t ON s.topic_id = t.id
            WHERE t.project_id = ? AND s.user_id = ?
        """, (project_id, user_id))
        total_study_time = (await cursor.fetchone())[0] or 0
        
        # Topics count
        cursor = await db.execute("""
            SELECT COUNT(*) FROM topics WHERE project_id = ?
        """, (project_id,))
        topics_count = (await cursor.fetchone())[0]
        
        # Average confidence
        cursor = await db.execute("""
            SELECT AVG(confidence_level) FROM topics WHERE project_id = ?
        """, (project_id,))
        average_confidence = (await cursor.fetchone())[0] or 0.0
        
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
    async with aiosqlite.connect(settings.DATABASE_URL) as db:
        cursor = await db.execute("""
            SELECT t.id, t.name, p.name, t.stuck_count, t.confidence_level
            FROM topics t
            JOIN projects p ON t.project_id = p.id
            WHERE p.user_id = ? AND t.stuck_count > 0
            ORDER BY t.stuck_count DESC
            LIMIT ?
        """, (user_id, limit))
        rows = await cursor.fetchall()
        
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