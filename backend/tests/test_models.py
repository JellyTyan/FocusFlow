import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from models.project import ProjectCreate
from models.topic import TopicCreate, TopicUpdate
from models.session import SessionStart

def test_project_create_valid():
    """Test valid project creation"""
    future_date = datetime.now() + timedelta(days=30)
    project = ProjectCreate(
        name="Test Project",
        subject="Math",
        deadline=future_date,
        topics=["Topic 1", "Topic 2"]
    )
    assert project.name == "Test Project"
    assert project.subject == "Math"

def test_project_create_past_deadline():
    """Test project with past deadline fails"""
    past_date = datetime.now() - timedelta(days=1)
    with pytest.raises(ValidationError):
        ProjectCreate(
            name="Test Project",
            subject="Math",
            deadline=past_date
        )

def test_topic_create_valid():
    """Test valid topic creation"""
    topic = TopicCreate(name="Photosynthesis", confidence_level=3)
    assert topic.name == "Photosynthesis"
    assert topic.confidence_level == 3

def test_topic_invalid_confidence():
    """Test topic with invalid confidence level"""
    with pytest.raises(ValidationError):
        TopicCreate(name="Test", confidence_level=6)
    
    with pytest.raises(ValidationError):
        TopicCreate(name="Test", confidence_level=0)

def test_topic_update():
    """Test topic update"""
    update = TopicUpdate(confidence_level=4)
    assert update.confidence_level == 4