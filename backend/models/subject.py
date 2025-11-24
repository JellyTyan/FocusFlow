from pydantic import BaseModel, validator
from datetime import datetime
from uuid import UUID

class SubjectBase(BaseModel):
    name: str
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Subject name cannot be empty')
        return v.strip()

class SubjectCreate(SubjectBase):
    pass

class Subject(SubjectBase):
    id: UUID
    user_id: UUID
    created_at: datetime

