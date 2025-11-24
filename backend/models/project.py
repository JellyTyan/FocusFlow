from pydantic import BaseModel, validator
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from config import settings


class ProjectBase(BaseModel):
    name: str
    subject: str
    deadline: datetime

    @validator('deadline')
    def validate_deadline(cls, v):
        if v <= datetime.now():
            raise ValueError('Deadline must be in the future')
        return v

    @validator('name', 'subject')
    def validate_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Field cannot be empty')
        return v.strip()

class ProjectCreate(ProjectBase):
    topics: List[str] = []  # List of topic names

class Project(ProjectBase):
    id: UUID
    created_at: datetime
    topics: List = []  # Will be populated with Topic objects
    progress: float = 0.0
    completed: bool = False

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: Optional[bool] = None
