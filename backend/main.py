from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import traceback
import os

from routers.projects import router as projects_router
from routers.auth import router as auth_router
from routers.user import router as user_router
from routers.topics import router as topics_router
from routers.sessions import router as sessions_router
from routers.ai_chat import router as ai_chat_router
from routers.ai import router as ai_router
from routers.stats import router as stats_router
from routers.subjects import router as subjects_router
from routers.logs import router as logs_router
from database.user_db import create_db_and_tables
from database.connection import init_db
from exceptions import (
    FocusFlowException,
    exception_handler,
    AIUnavailableError,
    AITimeoutError,
    AIRateLimitError,
    AIValidationError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        logger.info("Baza danych zainicjalizowana pomyślnie")
    except Exception as e:
        logger.error(f"Nie udało się zainicjalizować bazy danych: {e}", exc_info=True)
    yield

app = FastAPI(lifespan=lifespan, title="FocusFlow API", version="1.0.0")

CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS", "*")
if CORS_ORIGINS_ENV == "*":
    CORS_ORIGINS = ["*"]
    CORS_CREDENTIALS = False
else:
    CORS_ORIGINS = CORS_ORIGINS_ENV.split(",")
    CORS_CREDENTIALS = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Błąd walidacji: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, HTTPException):
        logger.warning(f"HTTPException: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    logger.error(f"Nieobsłużony wyjątek: {exc}", exc_info=True)

    if isinstance(exc, (FocusFlowException, AIUnavailableError, AITimeoutError, AIRateLimitError, AIValidationError)):
        status_code = exc.status_code
        detail = exc.message
    else:
        status_code = 500
        detail = str(exc) if str(exc) else "Wewnętrzny błąd serwera"
        logger.error(f"Traceback: {traceback.format_exc()}")

    return JSONResponse(
        status_code=status_code,
        content={"detail": detail}
    )

app.add_exception_handler(FocusFlowException, exception_handler)

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "FocusFlow API"}

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(user_router, prefix="/api/user", tags=["user"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(topics_router, prefix="/api", tags=["topics"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(ai_chat_router, prefix="/api", tags=["ai-chat"])
app.include_router(ai_router, prefix="/api", tags=["ai"])
app.include_router(stats_router, prefix="/api", tags=["stats"])
app.include_router(subjects_router, prefix="/api/subjects", tags=["subjects"])
app.include_router(logs_router, prefix="/api", tags=["logs"])
