from pydantic import BaseModel
from typing import List
from uuid import UUID

class StatsOverview(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_study_time: int  # seconds
    total_projects: int
    total_topics: int

class ProjectStats(BaseModel):
    project_id: UUID
    total_sessions: int
    completed_sessions: int
    total_study_time: int
    topics_count: int
    average_confidence: float

class StuckTopic(BaseModel):
    topic_id: UUID
    topic_name: str
    project_name: str
    stuck_count: int
    confidence_level: int

class StuckTopics(BaseModel):
    topics: List[StuckTopic]