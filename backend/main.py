from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from routers.projects import router as projects_router
from routers.auth import router as auth_router
from routers.topics import router as topics_router
from routers.sessions import router as sessions_router
from routers.ai_chat import router as ai_chat_router
from routers.stats import router as stats_router
from database.connection import init_db
from exceptions import FocusFlowException, exception_handler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan, title="FocusFlow API", version="1.0.0")

# Add exception handlers
app.add_exception_handler(FocusFlowException, exception_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["auth"])
app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
app.include_router(topics_router, prefix="/api", tags=["topics"])
app.include_router(sessions_router, prefix="/api", tags=["sessions"])
app.include_router(ai_chat_router, prefix="/api", tags=["ai-chat"])
app.include_router(stats_router, prefix="/api", tags=["stats"])
