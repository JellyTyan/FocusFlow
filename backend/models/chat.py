from pydantic import BaseModel
from datetime import datetime
from typing import List
from uuid import UUID
from enum import Enum

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"

class ChatMessageCreate(BaseModel):
    session_id: UUID
    content: str

class ChatMessage(BaseModel):
    id: UUID
    session_id: UUID
    role: MessageRole
    content: str
    timestamp: datetime

class ChatHistory(BaseModel):
    session_id: UUID
    messages: List[ChatMessage]