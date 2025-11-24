from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.topic import Topic, TopicCreate, TopicUpdate, TopicPriority
from database import topic_repository as db
from dependencies import get_current_user

router = APIRouter()

@router.get("/projects/{project_id}/topics", response_model=List[Topic])
async def get_project_topics(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get all topics for a project"""
    return await db.get_project_topics(project_id, current_user["id"])

@router.post("/projects/{project_id}/topics", response_model=Topic)
async def create_topic(project_id: str, topic: TopicCreate, current_user: dict = Depends(get_current_user)):
    """Create new topic"""
    return await db.create_topic(project_id, topic, current_user["id"])

@router.put("/topics/{topic_id}", response_model=Topic)
async def update_topic(topic_id: str, update_data: TopicUpdate, current_user: dict = Depends(get_current_user)):
    """Update topic"""
    topic = await db.update_topic(topic_id, update_data, current_user["id"])
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.delete("/topics/{topic_id}")
async def delete_topic(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Delete topic"""
    success = await db.delete_topic(topic_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Topic not found")
    return {"message": "Topic deleted"}

@router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Get topic by ID"""
    topic = await db.get_topic(topic_id, current_user["id"])
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/topics/{topic_id}/priority", response_model=TopicPriority)
async def get_topic_priority(topic_id: str, current_user: dict = Depends(get_current_user)):
    """Get topic priority score"""
    priority_score = await db.get_topic_priority(topic_id, current_user["id"])
    return TopicPriority(topic_id=topic_id, priority_score=priority_score)