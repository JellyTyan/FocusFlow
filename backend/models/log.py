from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class ClientLogCreate(BaseModel):
    level: str = Field(..., pattern='^(info|warn|error)$')
    message: str
    timestamp: str
    meta: Optional[Dict[str, Any]] = None
    path: Optional[str] = None
