from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional
from uuid import UUID
from config import settings

class TopicBase(BaseModel):
    name: str
    confidence_level: int = 1
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        if not (settings.MIN_CONFIDENCE_LEVEL <= v <= settings.MAX_CONFIDENCE_LEVEL):
            raise ValueError(f'Confidence level must be between {settings.MIN_CONFIDENCE_LEVEL} and {settings.MAX_CONFIDENCE_LEVEL}')
        return v
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Topic name cannot be empty')
        return v.strip()

class TopicCreate(TopicBase):
    pass

class TopicUpdate(BaseModel):
    name: Optional[str] = None
    confidence_level: Optional[int] = None
    completed: Optional[bool] = None
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Topic name cannot be empty')
        return v.strip() if v else v
    
    @validator('confidence_level')
    def validate_confidence_level(cls, v):
        if v is not None and not (settings.MIN_CONFIDENCE_LEVEL <= v <= settings.MAX_CONFIDENCE_LEVEL):
            raise ValueError(f'Confidence level must be between {settings.MIN_CONFIDENCE_LEVEL} and {settings.MAX_CONFIDENCE_LEVEL}')
        return v

class Topic(TopicBase):
    id: UUID
    project_id: UUID
    priority_score: float = 0.0
    stuck_count: int = 0
    created_at: datetime
    completed: bool = False

class TopicPriority(BaseModel):
    topic_id: UUID
    priority_score: float