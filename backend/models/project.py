from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

class TopicBase(BaseModel):
    name: str
    confidence_level: int = 1  # 1-5 stars

class Topic(TopicBase):
    id: UUID
    project_id: UUID
    priority_score: float = 0.0
    stuck_count: int = 0
    created_at: datetime

class ProjectBase(BaseModel):
    name: str
    subject: str
    deadline: datetime

class ProjectCreate(ProjectBase):
    topics: List[str] = []  # List of topic names

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    topics: List[Topic] = []
    progress: float = 0.0

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    deadline: Optional[datetime] = None
