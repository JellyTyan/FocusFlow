import os
from typing import List
from models.chat import ChatMessage, MessageRole
import logging

from services.g4f_service import get_g4f_service
from exceptions import (
    AIUnavailableError,
    AITimeoutError,
    AIRateLimitError,
    AIValidationError,
)

logger = logging.getLogger(__name__)


async def generate_ai_response(
    user_message: str,
    topic_name: str,
    project_name: str,
    chat_history: List[ChatMessage]
) -> str:
    """
    Generuje odpowiedź AI używając serwisu g4f z kontekstem.
    
    Args:
        user_message: Wiadomość/pytanie użytkownika
        topic_name: Aktualnie studiowany temat
        project_name: Nazwa projektu/egzaminu
        chat_history: Poprzednie wiadomości czatu dla kontekstu
        
    Returns:
        Wygenerowany tekst odpowiedzi AI
        
    Raises:
        AIUnavailableError: Gdy serwis AI jest niedostępny
        AITimeoutError: Gdy żądanie przekroczy limit czasu
        AIRateLimitError: Gdy przekroczono limit żądań
        AIValidationError: Gdy walidacja wejścia nie powiodła się
    """
    try:
        g4f_service = get_g4f_service()
        
        system_prompt = f"""Jesteś asystentem AI w aplikacji FocusFlow. 
Użytkownik studiuje temat: "{topic_name}" 
w ramach projektu: "{project_name}".

Twoim zadaniem jest:
- Dawać krótkie, zrozumiałe wyjaśnienia
- Nie rozpraszać od nauki
- Motywować do kontynuacji sesji
- Odpowiadać po polsku

Użytkownik utknął i potrzebuje pomocy."""
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg.role.value,
                "content": msg.content
            })
        
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        logger.info(f"Żądanie AI dla tematu: {topic_name}, wiadomość: {user_message[:50]}...")
        
        response = await g4f_service.generate_chat(
            messages=messages,
            stream=False,
            timeout=60.0,
        )
        
        logger.info(f"Odpowiedź AI wygenerowana pomyślnie dla tematu: {topic_name}")
        return response or f"Pomogę Ci zrozumieć temat '{topic_name}'. Co dokładnie sprawia trudności?"
        
    except (AIUnavailableError, AITimeoutError, AIRateLimitError) as e:
        logger.warning(f"Błąd serwisu AI: {str(e)}, używam odpowiedzi zapasowej")
        return f"Pomogę Ci zrozumieć temat '{topic_name}'. Co dokładnie sprawia trudności?"
    
    except AIValidationError as e:
        logger.error(f"Błąd walidacji AI: {str(e)}")
        raise
    
    except Exception as e:
        logger.error(f"Nieoczekiwany błąd w generowaniu AI: {str(e)}", exc_info=True)
        return f"Pomogę Ci zrozumieć temat '{topic_name}'. Co dokładnie sprawia trudności?"