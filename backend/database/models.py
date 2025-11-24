from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.user_db import Base
from uuid import uuid4


class Project(Base):
    __tablename__ = "projects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    subject = Column(String(255), nullable=False)
    deadline = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    progress = Column(Float, default=0.0)
    completed = Column(Boolean, default=False)
    
    # Relationships
    topics = relationship("Topic", back_populates="project", cascade="all, delete-orphan")


class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    confidence_level = Column(Integer, default=1)
    priority_score = Column(Float, default=0.0)
    stuck_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    completed = Column(Boolean, default=False)
    
    # Relationships
    project = relationship("Project", back_populates="topics")
    sessions = relationship("Session", back_populates="topic", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    status = Column(String(20), nullable=False)
    start_time = Column(DateTime, nullable=False)
    pause_time = Column(DateTime, nullable=True)
    resume_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, default=0)
    stuck_moments = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    
    # Relationships
    topic = relationship("Topic", back_populates="sessions")
    chat_messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    session = relationship("Session", back_populates="chat_messages")


class Subject(Base):
    __tablename__ = "subjects"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class ClientLog(Base):
    __tablename__ = "client_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    level = Column(String(20), nullable=False)
    message = Column(Text, nullable=False)
    meta = Column(Text, nullable=True)
    timestamp = Column(DateTime, nullable=False)
    user_agent = Column(String(500), nullable=True)
    path = Column(String(500), nullable=True)
    client_ip = Column(String(50), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

