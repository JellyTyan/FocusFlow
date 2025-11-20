from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class FocusFlowException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ProjectNotFoundError(FocusFlowException):
    def __init__(self, project_id: str):
        super().__init__(f"Project {project_id} not found", 404)

class UnauthorizedAccessError(FocusFlowException):
    def __init__(self, resource: str):
        super().__init__(f"Unauthorized access to {resource}", 403)

class ValidationError(FocusFlowException):
    def __init__(self, message: str):
        super().__init__(message, 400)

async def exception_handler(request: Request, exc: FocusFlowException):
    logger.error(f"FocusFlow error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )