import aiosqlite
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from uuid import uuid4

SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
DATABASE_URL = "focusflow.db"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        return email
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

async def create_user(email: str, password: str, name: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        # Check if user exists
        cursor = await db.execute("SELECT id FROM users WHERE email = ?", (email,))
        if await cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        user_id = str(uuid4())
        hashed_password = get_password_hash(password)
        now = datetime.now().isoformat()
        
        await db.execute(
            "INSERT INTO users (id, email, name, hashed_password, created_at) VALUES (?, ?, ?, ?, ?)",
            (user_id, email, name, hashed_password, now)
        )
        await db.commit()
        
        return {
            "id": user_id,
            "email": email,
            "name": name,
            "created_at": now
        }

async def authenticate_user(email: str, password: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT id, email, name, hashed_password, created_at FROM users WHERE email = ?",
            (email,)
        )
        user_row = await cursor.fetchone()
        
        if not user_row:
            return False
        
        if not verify_password(password, user_row[3]):
            return False
        
        return {
            "id": user_row[0],
            "email": user_row[1],
            "name": user_row[2],
            "created_at": user_row[4]
        }

async def get_user_by_email(email: str):
    async with aiosqlite.connect(DATABASE_URL) as db:
        cursor = await db.execute(
            "SELECT id, email, name, created_at FROM users WHERE email = ?",
            (email,)
        )
        user_row = await cursor.fetchone()
        
        if not user_row:
            return None
        
        return {
            "id": user_row[0],
            "email": user_row[1],
            "name": user_row[2],
            "created_at": user_row[3]
        }