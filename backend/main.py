from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.projects import router as projects_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(projects_router, prefix="/api/projects", tags=["projects"])
