from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: UUID
    email: str
    name: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"