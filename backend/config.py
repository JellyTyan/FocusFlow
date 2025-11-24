import os
from typing import Optional

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "mysql+aiomysql://focusflow:focusflow@localhost:3306/focusflow")
    
    MIN_CONFIDENCE_LEVEL: int = 1
    MAX_CONFIDENCE_LEVEL: int = 5
    
    G4F_ENABLED: bool = os.getenv("G4F_ENABLED", "true").lower() == "true"
    G4F_DEFAULT_MODEL: str = os.getenv("G4F_DEFAULT_MODEL", "gpt-5-mini")
    G4F_TIMEOUT: float = float(os.getenv("G4F_TIMEOUT", "60.0"))
    _fallback_models_env = os.getenv("G4F_FALLBACK_MODELS")
    G4F_FALLBACK_MODELS: list = (
        _fallback_models_env.split(",") if _fallback_models_env 
        else ["gpt-5-nano", "gemini-2.5-flash"]
    )
    _blocked_providers_env = os.getenv("G4F_BLOCKED_PROVIDERS")
    G4F_BLOCKED_PROVIDERS: list = (
        _blocked_providers_env.split(",") if _blocked_providers_env 
        else ["AirForce"]
    )
    G4F_USE_BROWSER_HEADERS: bool = os.getenv("G4F_USE_BROWSER_HEADERS", "true").lower() == "true"
    G4F_USER_AGENT: str = os.getenv(
        "G4F_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

settings = Settings()