from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import auth

security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    email = auth.verify_token(token)
    user = await auth.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user