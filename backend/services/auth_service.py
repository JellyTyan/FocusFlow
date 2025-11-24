from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.user_db import User
from database.connection import get_db
from config import settings
import logging

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def create_user(email: str, password: str, name: str):
    async for session in get_db():
        result = await session.execute(
            select(User.id).where(User.email == email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = str(uuid4())
        hashed_password = get_password_hash(password)
        now = datetime.now()
        
        user_model = User(
            id=user_id,
            email=email,
            name=name,
            hashed_password=hashed_password,
            created_at=now
        )
        session.add(user_model)
        await session.commit()
        
        return {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": now.isoformat()
        }

async def authenticate_user(email: str, password: str):
    async for session in get_db():
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return False
        
        if not verify_password(password, user_model.hashed_password):
            return False
        
        return {
            "id": str(user_model.id),
            "email": user_model.email,
            "name": user_model.name,
            "created_at": user_model.created_at.isoformat() if user_model.created_at else None
        }

async def get_user_by_email(email: str):
    async for session in get_db():
        result = await session.execute(
            select(User).where(User.email == email)
        )
        user_model = result.scalar_one_or_none()
        
        if not user_model:
            return None
        
        return {
            "id": str(user_model.id),
            "email": user_model.email,
            "name": user_model.name,
            "created_at": user_model.created_at.isoformat() if user_model.created_at else None
        }
