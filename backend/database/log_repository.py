import json
from datetime import datetime
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import ClientLog as ClientLogModel
from database.connection import get_db
from models.log import ClientLogCreate

async def insert_client_log(log: ClientLogCreate, user_agent: str | None, path: str | None, client_ip: str | None):
    log_id = str(uuid4())
    created_at = datetime.utcnow()
    async for session in get_db():
        log_model = ClientLogModel(
            id=log_id,
            level=log.level,
            message=log.message,
            meta=json.dumps(log.meta or {}),
            timestamp=datetime.fromisoformat(log.timestamp),
            user_agent=user_agent,
            path=path,
            client_ip=client_ip,
            created_at=created_at
        )
        session.add(log_model)
        await session.commit()
        break
