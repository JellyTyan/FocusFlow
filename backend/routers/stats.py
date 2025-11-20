from fastapi import APIRouter, HTTPException, Depends
from models.stats import StatsOverview, ProjectStats, StuckTopics
from services import stats
from dependencies import get_current_user

router = APIRouter()

@router.get("/stats/overview", response_model=StatsOverview)
async def get_overview(current_user: dict = Depends(get_current_user)):
    """Get overall statistics"""
    return await stats.get_overview_stats(current_user["id"])

@router.get("/stats/projects/{project_id}", response_model=ProjectStats)
async def get_project_stats(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get project statistics"""
    project_stats = await stats.get_project_stats(project_id, current_user["id"])
    if not project_stats:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_stats

@router.get("/stats/stuck-topics", response_model=StuckTopics)
async def get_stuck_topics(current_user: dict = Depends(get_current_user)):
    """Get topics with most stuck moments"""
    return await stats.get_stuck_topics(current_user["id"])