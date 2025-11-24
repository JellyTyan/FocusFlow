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
        super().__init__(f"Projekt {project_id} nie został znaleziony", 404)

class UnauthorizedAccessError(FocusFlowException):
    def __init__(self, resource: str):
        super().__init__(f"Brak autoryzacji do zasobu {resource}", 403)

class ValidationError(FocusFlowException):
    def __init__(self, message: str):
        super().__init__(message, 400)

class AIUnavailableError(FocusFlowException):
    def __init__(self, message: str = "Serwis AI jest obecnie niedostępny"):
        super().__init__(message, 503)

class AITimeoutError(FocusFlowException):
    def __init__(self, message: str = "Żądanie AI przekroczyło limit czasu"):
        super().__init__(message, 504)

class AIRateLimitError(FocusFlowException):
    def __init__(self, message: str = "Przekroczono limit żądań AI. Spróbuj ponownie później"):
        super().__init__(message, 429)

class AIValidationError(FocusFlowException):
    def __init__(self, message: str = "Nieprawidłowe żądanie AI"):
        super().__init__(message, 400)

async def exception_handler(request: Request, exc: FocusFlowException):
    logger.error(f"Błąd FocusFlow: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )