from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"

class SessionStart(BaseModel):
    topic_id: UUID

class Session(BaseModel):
    id: UUID
    topic_id: UUID
    user_id: UUID
    status: SessionStatus
    start_time: datetime
    pause_time: Optional[datetime] = None
    resume_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: int = 0  # seconds
    stuck_moments: int = 0
    completed: bool = False

class SessionStatusResponse(BaseModel):
    id: UUID
    status: SessionStatus
    duration: int
    stuck_moments: int
    completed: bool