from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.project import Project, ProjectCreate, ProjectUpdate
from database import project_repository as db
from dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[Project])
async def get_all_projects(current_user: dict = Depends(get_current_user)):
    """Get all projects"""
    try:
        logger.info(f"Fetching projects for user: {current_user.get('id')}")
        projects = await db.get_all_projects(current_user["id"])
        logger.info(f"Found {len(projects)} projects")
        return projects
    except Exception as e:
        logger.error(f"Error fetching projects: {e}", exc_info=True)
        raise

@router.post("/", response_model=Project)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    """Create new project"""
    return await db.create_project(project, current_user["id"])

@router.get("/{project_id}", response_model=Project)
async def get_project_by_id(project_id: str, current_user: dict = Depends(get_current_user)):
    """Get project by ID"""
    project = await db.get_project(project_id, current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
async def update_project_by_id(project_id: str, update_data: ProjectUpdate, current_user: dict = Depends(get_current_user)):
    """Update project"""
    project = await db.update_project(project_id, update_data, current_user["id"])
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
async def delete_project_by_id(project_id: str, current_user: dict = Depends(get_current_user)):
    """Delete project"""
    success = await db.delete_project(project_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}