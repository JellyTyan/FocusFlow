from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from models.user import UserCreate, UserLogin, User, Token
import auth

router = APIRouter()

@router.post("/register", response_model=User)
async def register(user_data: UserCreate):
    """Register new user"""
    user = await auth.create_user(user_data.email, user_data.password, user_data.name)
    return User(
        id=user["id"],
        email=user["email"],
        name=user["name"],
        created_at=user["created_at"]
    )

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user"""
    user = await auth.authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}