from fastapi import APIRouter, HTTPException, Depends
from typing import List
from models.subject import Subject, SubjectCreate
from database import subject_repository as db
from dependencies import get_current_user

router = APIRouter()

@router.get("/", response_model=List[Subject])
async def get_all_subjects(current_user: dict = Depends(get_current_user)):
    """Get all user subjects"""
    return await db.get_all_subjects(current_user["id"])

@router.post("/", response_model=Subject)
async def create_subject(subject: SubjectCreate, current_user: dict = Depends(get_current_user)):
    """Create new subject"""
    return await db.create_subject(subject, current_user["id"])

@router.delete("/{subject_id}")
async def delete_subject(subject_id: str, current_user: dict = Depends(get_current_user)):
    """Delete subject"""
    success = await db.delete_subject(subject_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Subject not found")
    return {"message": "Subject deleted"}

