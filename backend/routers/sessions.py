from fastapi import APIRouter, HTTPException, Depends
from models.session import Session, SessionStart, SessionStatusResponse
from database import session_repository as db
from dependencies import get_current_user

router = APIRouter()

@router.post("/sessions/start", response_model=Session)
async def start_session(session_data: SessionStart, current_user: dict = Depends(get_current_user)):
    """Start new learning session"""
    return await db.start_session(session_data, current_user["id"])

@router.put("/sessions/{session_id}/pause", response_model=Session)
async def pause_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Pause active session"""
    session = await db.pause_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}/resume", response_model=Session)
async def resume_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Resume paused session"""
    session = await db.resume_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/sessions/{session_id}/complete", response_model=Session)
async def complete_session(session_id: str, current_user: dict = Depends(get_current_user)):
    """Complete session"""
    session = await db.complete_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(session_id: str, current_user: dict = Depends(get_current_user)):
    """Get session status"""
    status = await db.get_session_status(session_id, current_user["id"])
    if not status:
        raise HTTPException(status_code=404, detail="Session not found")
    return status