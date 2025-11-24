from fastapi import APIRouter, Request, BackgroundTasks, status
from models.log import ClientLogCreate
from database.log_repository import insert_client_log

router = APIRouter()

async def _store_log(log: ClientLogCreate, request: Request):
    user_agent = request.headers.get('user-agent')
    path = log.path or request.headers.get('referer')
    client_ip = request.client.host if request.client else None
    await insert_client_log(log, user_agent, path, client_ip)

@router.post('/logs', status_code=status.HTTP_201_CREATED)
async def ingest_log(log: ClientLogCreate, request: Request, background_tasks: BackgroundTasks):
    background_tasks.add_task(_store_log, log, request)
    return {'status': 'ok'}
