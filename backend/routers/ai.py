from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, validator
from typing import List, Optional
import logging
import json

from services.g4f_service import get_g4f_service, G4FService
from exceptions import (
    AIUnavailableError,
    AITimeoutError,
    AIRateLimitError,
    AIValidationError,
)
from dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class Message(BaseModel):
    role: str = Field(..., description="Rola wiadomości: 'user' lub 'assistant'")
    content: str = Field(..., min_length=1, max_length=10000, description="Treść wiadomości")
    
    @validator('role')
    def validate_role(cls, v):
        if v not in ['user', 'assistant', 'system']:
            raise ValueError("Rola musi być 'user', 'assistant' lub 'system'")
        return v


class GenerateRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1, description="Lista wiadomości czatu")
    model: Optional[str] = Field(None, description="Nazwa modelu (opcjonalne)")
    timeout: Optional[float] = Field(None, ge=1.0, le=300.0, description="Timeout w sekundach (1-300)")
    stream: bool = Field(False, description="Czy streamować odpowiedź")


class GenerateResponse(BaseModel):
    content: str = Field(..., description="Wygenerowany tekst odpowiedzi")
    model: str = Field(..., description="Użyty model")
    finish_reason: Optional[str] = Field(None, description="Powód zakończenia")


@router.post("/ai/generate", response_model=GenerateResponse)
async def generate_ai(
    request: GenerateRequest,
    current_user: dict = Depends(get_current_user),
    g4f_service: G4FService = Depends(get_g4f_service),
):
    if not g4f_service.enabled or not g4f_service.client:
        logger.warning(f"Serwis G4F niedostępny dla użytkownika {current_user.get('id')}")
        raise HTTPException(
            status_code=503,
            detail="Serwis AI jest obecnie niedostępny. Spróbuj ponownie później."
        )
    
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        content = await g4f_service.generate_chat(
            messages=messages,
            model=request.model,
            stream=False,
            timeout=request.timeout,
        )
        
        logger.info(f"Generowanie AI zakończone dla użytkownika {current_user.get('id')}")
        
        return GenerateResponse(
            content=content or "",
            model=request.model or g4f_service.default_model,
            finish_reason="stop",
        )
        
    except AIValidationError as e:
        logger.warning(f"Błąd walidacji dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except AIRateLimitError as e:
        logger.warning(f"Limit żądań dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=429, detail=str(e))
    except AITimeoutError as e:
        logger.warning(f"Timeout dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=504, detail=str(e))
    except AIUnavailableError as e:
        logger.error(f"AI niedostępne dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd w generowaniu AI: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")


@router.post("/ai/stream")
async def stream_ai(
    request: GenerateRequest,
    current_user: dict = Depends(get_current_user),
    g4f_service: G4FService = Depends(get_g4f_service),
):
    try:
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        async def generate_stream():
            try:
                chunk_count = 0
                async for chunk in g4f_service.stream_chat(
                    messages=messages,
                    model=request.model,
                    timeout=request.timeout,
                ):
                    if chunk:
                        chunk_count += 1
                        chunk_size = 10
                        for i in range(0, len(chunk), chunk_size):
                            sub_chunk = chunk[i:i + chunk_size]
                            if sub_chunk:
                                data = json.dumps({"content": sub_chunk})
                                yield f"data: {data}\n\n"
                
                logger.info(f"Streaming zakończony, łącznie chunków: {chunk_count}")
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                logger.error(f"Błąd streamingu: {str(e)}", exc_info=True)
                error_data = json.dumps({"error": str(e)})
                yield f"data: {error_data}\n\n"
                raise
        
        logger.info(f"Streaming AI rozpoczęty dla użytkownika {current_user.get('id')}")
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            }
        )
        
    except AIValidationError as e:
        logger.warning(f"Błąd walidacji dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except AIRateLimitError as e:
        logger.warning(f"Limit żądań dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=429, detail=str(e))
    except AITimeoutError as e:
        logger.warning(f"Timeout dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=504, detail=str(e))
    except AIUnavailableError as e:
        logger.error(f"AI niedostępne dla użytkownika {current_user.get('id')}: {str(e)}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd w streamingu AI: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Wewnętrzny błąd serwera")


@router.get("/ai/health")
async def ai_health(g4f_service: G4FService = Depends(get_g4f_service)):
    return {
        "enabled": g4f_service.enabled,
        "available": g4f_service.enabled and g4f_service.client is not None,
        "default_model": g4f_service.default_model if g4f_service.enabled else None,
    }

