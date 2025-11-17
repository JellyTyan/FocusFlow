from fastapi import APIRouter, HTTPException
from typing import List
from models.project import Project, ProjectCreate, ProjectUpdate
import database as db

router = APIRouter()

@router.get("/", response_model=List[Project])
def get_all_projects():
    """Получить все проекты"""
    return db.get_all_projects()

@router.post("/", response_model=Project)
def create_project(project: ProjectCreate):
    """Создать новый проект"""
    return db.create_project(project)

@router.get("/{project_id}", response_model=Project)
def get_project_by_id(project_id: str):
    """Получить проект по ID"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project

@router.put("/{project_id}", response_model=Project)
def update_project_by_id(project_id: str, update_data: ProjectUpdate):
    """Обновить проект"""
    project = db.update_project(project_id, update_data)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return project

@router.delete("/{project_id}")
def delete_project_by_id(project_id: str):
    """Удалить проект"""
    success = db.delete_project(project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Проект не найден")
    return {"message": "Проект удален"}