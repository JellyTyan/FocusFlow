from fastapi import APIRouter, HTTPException
from typing import List
from models.project import Project, ProjectCreate, ProjectUpdate
import database as db

router = APIRouter()

@router.get("/", response_model=List[Project])
def get_all_projects():
    """Get all projects"""
    return db.get_all_projects()

@router.post("/", response_model=Project)
def create_project(project: ProjectCreate):
    """Create new project"""
    return db.create_project(project)

@router.get("/{project_id}", response_model=Project)
def get_project_by_id(project_id: str):
    """Get project by ID"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=Project)
def update_project_by_id(project_id: str, update_data: ProjectUpdate):
    """Update project"""
    project = db.update_project(project_id, update_data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}")
def delete_project_by_id(project_id: str):
    """Delete project"""
    success = db.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"message": "Project deleted"}