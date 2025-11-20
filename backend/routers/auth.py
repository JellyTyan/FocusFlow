from fastapi import APIRouter, HTTPException, status
from datetime import timedelta, datetime
from uuid import UUID
from models.user import UserCreate, UserLogin, User, Token
from services.auth_service import create_user, authenticate_user, create_access_token
from config import settings

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Register new user"""
    user = await create_user(user_data.email, user_data.password, user_data.name)
    return User(
        id=UUID(user["id"]),
        email=user["email"],
        name=user["name"],
        created_at=datetime.fromisoformat(user["created_at"])
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    user = await authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}