import os
from typing import Optional

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "focusflow.db")
    
    # Validation constants
    MIN_CONFIDENCE_LEVEL: int = 1
    MAX_CONFIDENCE_LEVEL: int = 5

settings = Settings()