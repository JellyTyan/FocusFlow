from fastapi import Depends
from auth.users import current_active_user
from database.user_db import User

async def get_current_user(user: User = Depends(current_active_user)):
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "created_at": user.created_at.isoformat() if hasattr(user, 'created_at') and user.created_at else None
    }
