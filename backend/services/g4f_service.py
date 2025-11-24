"""
Serwis g4f - asynchroniczny wrapper dla integracji GPT4Free.

Zapewnia produkcyjny interfejs do g4f z:
- Obsługą timeoutów
- Retry z exponential backoff
- Walidacją i sanitizacją wejścia
- Wsparciem dla streamingu i non-streaming
"""

import asyncio
import logging
import re
from typing import List, Dict, Optional, AsyncIterator, Any

logger = logging.getLogger(__name__)

try:
    import g4f
    logger.info(f"Moduł g4f zaimportowany, wersja: {getattr(g4f, '__version__', 'nieznana')}")
    from g4f.client import AsyncClient
    logger.info("g4f.client.AsyncClient zaimportowany pomyślnie")
    try:
        from g4f import Provider
        PROVIDERS_AVAILABLE = True
        logger.info("g4f.Provider zaimportowany pomyślnie")
    except ImportError:
        PROVIDERS_AVAILABLE = False
        Provider = None
        logger.warning("g4f.Provider niedostępny, użycie automatycznego wyboru providera")
    G4F_AVAILABLE = True
    logger.info("g4f zaimportowany i dostępny")
except ImportError as e:
    G4F_AVAILABLE = False
    PROVIDERS_AVAILABLE = False
    AsyncClient = None
    Provider = None
    logger.warning(f"Import g4f nie powiódł się (ImportError): {str(e)}", exc_info=True)
except Exception as e:
    G4F_AVAILABLE = False
    PROVIDERS_AVAILABLE = False
    AsyncClient = None
    Provider = None
    logger.error(f"Błąd importu g4f (Exception): {str(e)}", exc_info=True)

from exceptions import (
    AIUnavailableError,
    AITimeoutError,
    AIRateLimitError,
    AIValidationError,
)

DEFAULT_MODEL = "gpt-3.5-turbo"
DEFAULT_TIMEOUT = 60.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.0
DEFAULT_MAX_BACKOFF = 30.0
PROMPT_INJECTION_PATTERNS = [
    r'ignore\s+(previous|all|above)\s+(instructions|prompts?)',
    r'forget\s+(previous|all|above)',
    r'you\s+are\s+now',
    r'act\s+as\s+if',
    r'pretend\s+to\s+be',
    r'disregard\s+(previous|all)',
    r'new\s+instructions?:',
    r'system\s*:',
    r'<\|system\|>',
    r'<\|assistant\|>',
]


class G4FService:
    """
    Asynchroniczny wrapper serwisu g4f z niezawodnością produkcyjną.
    
    Funkcje:
    - Automatyczne retry z exponential backoff
    - Obsługa timeoutów
    - Walidacja i sanitizacja wejścia
    - Wykrywanie limitów żądań
    - Wsparcie dla streamingu
    """
    
    def __init__(
        self,
        enabled: bool = True,
        default_model: str = DEFAULT_MODEL,
        default_timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        max_backoff: float = DEFAULT_MAX_BACKOFF,
        fallback_models: Optional[List[str]] = None,
        blocked_providers: Optional[List[str]] = None,
    ):
        """
        Inicjalizuje serwis G4F.
        
        Args:
            enabled: Czy g4f jest włączony (można wyłączyć przez config)
            default_model: Domyślny model do użycia
            default_timeout: Domyślny timeout w sekundach
            max_retries: Maksymalna liczba ponownych prób
            backoff_base: Podstawa dla exponential backoff
            max_backoff: Maksymalne opóźnienie backoff w sekundach
            fallback_models: Lista modeli zapasowych do wypróbowania jeśli główny model nie działa
            blocked_providers: Lista nazw providerów do zablokowania (np. ["AirForce"])
        """
        if not G4F_AVAILABLE:
            logger.warning("g4f niedostępny. Zainstaluj: pip install g4f==6.6.6")
            self.enabled = False
            self.client = None
            self.default_model = default_model
            self.default_timeout = default_timeout
            self.max_retries = max_retries
            self.backoff_base = backoff_base
            self.max_backoff = max_backoff
            self.fallback_models = fallback_models or []
            self.blocked_providers = blocked_providers or []
        else:
            self.enabled = enabled
            self.blocked_providers = blocked_providers or []
            
            if self.blocked_providers and PROVIDERS_AVAILABLE:
                try:
                    for provider_name in self.blocked_providers:
                        try:
                            provider_attr = getattr(Provider, provider_name, None)
                            if provider_attr:
                                if hasattr(provider_attr, 'working'):
                                    provider_attr.working = False
                                logger.info(f"Zablokowano providera: {provider_name}")
                        except Exception as e:
                            logger.warning(f"Nie udało się zablokować providera {provider_name}: {str(e)}")
                except Exception as e:
                    logger.warning(f"Błąd podczas blokowania providerów: {str(e)}")
            
            if enabled:
                try:
                    self.client = AsyncClient()
                    if self.blocked_providers:
                        logger.info(f"G4F AsyncClient zainicjalizowany z zablokowanymi providerami: {self.blocked_providers}")
                    else:
                        logger.info("G4F AsyncClient zainicjalizowany pomyślnie")
                except Exception as e:
                    logger.error(f"Nie udało się zainicjalizować G4F AsyncClient: {str(e)}", exc_info=True)
                    self.enabled = False
                    self.client = None
            else:
                self.client = None
                logger.info("Serwis G4F wyłączony przez config")
            
            self.default_model = default_model
            self.default_timeout = default_timeout
            self.max_retries = max_retries
            self.backoff_base = backoff_base
            self.max_backoff = max_backoff
            self.fallback_models = fallback_models or []
            
        logger.info(f"G4FService initialized: enabled={self.enabled}, model={default_model}, fallback_models={len(self.fallback_models)}, client_available={self.client is not None}, G4F_AVAILABLE={G4F_AVAILABLE}")
    
    def _validate_and_sanitize_prompt(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Waliduje i sanitizuje wiadomości użytkownika aby zapobiec prompt injection.
        
        Args:
            messages: Lista słowników wiadomości z 'role' i 'content'
            
        Returns:
            Zsanitizowane wiadomości
            
        Raises:
            AIValidationError: Jeśli wykryto prompt injection
        """
        sanitized = []
        
        for msg in messages:
            if not isinstance(msg, dict):
                raise AIValidationError("Invalid message format")
            
            role = msg.get('role', '').lower()
            content = msg.get('content', '')
            
            if not content or not isinstance(content, str):
                raise AIValidationError("Treść wiadomości musi być niepustym stringiem")
            
            content_lower = content.lower()
            for pattern in PROMPT_INJECTION_PATTERNS:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    logger.warning(f"Wykryto potencjalny prompt injection: {pattern}")
                    raise AIValidationError("Wykryto nieprawidłowe wejście. Proszę przeformułować wiadomość.")
            
            if len(content) > 10000:
                raise AIValidationError("Wiadomość zbyt długa (maksymalnie 10000 znaków)")
            
            content = re.sub(r'\s+', ' ', content.strip())
            
            sanitized.append({
                'role': role,
                'content': content
            })
        
        return sanitized
    
    async def _execute_with_retry(
        self,
        coro,
        timeout: float,
        operation_name: str = "Żądanie AI"
    ) -> Any:
        """
        Wykonuje asynchroniczną operację z retry i exponential backoff.
        
        Args:
            coro: Koro do wykonania
            timeout: Timeout w sekundach
            operation_name: Nazwa dla logowania
            
        Returns:
            Wynik koro
            
        Raises:
            AITimeoutError: Jeśli operacja przekroczy limit czasu
            AIUnavailableError: Jeśli wszystkie próby nie powiodły się
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    delay = min(
                        self.backoff_base ** attempt,
                        self.max_backoff
                    )
                    logger.info(f"{operation_name} - Ponowna próba {attempt}/{self.max_retries} po {delay:.1f}s")
                    await asyncio.sleep(delay)
                
                result = await asyncio.wait_for(coro, timeout=timeout)
                return result
                
            except asyncio.TimeoutError:
                last_error = AITimeoutError(f"{operation_name} przekroczyło limit czasu po {timeout}s")
                logger.warning(f"{operation_name} - Timeout przy próbie {attempt + 1}")
                
            except Exception as e:
                last_error = e
                error_msg = str(e).lower()
                
                if any(term in error_msg for term in ['rate limit', 'too many requests', '429']):
                    logger.warning(f"{operation_name} - Wykryto limit żądań")
                    raise AIRateLimitError(f"Przekroczono limit żądań: {str(e)}")
                
                if any(term in error_msg for term in ['provider', 'unavailable', '503', '502']):
                    logger.warning(f"{operation_name} - Błąd providera: {str(e)}")
                    if attempt < self.max_retries:
                        continue
                    raise AIUnavailableError(f"Provider AI niedostępny: {str(e)}")
                
                logger.error(f"{operation_name} - Błąd przy próbie {attempt + 1}: {str(e)}")
                
                if isinstance(e, AIValidationError):
                    raise
                
                if attempt < self.max_retries:
                    continue
                else:
                    raise AIUnavailableError(f"{operation_name} nie powiodło się po {self.max_retries + 1} próbach: {str(e)}")
        
        raise last_error or AIUnavailableError(f"{operation_name} nie powiodło się")
    
    async def generate_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        *,
        stream: bool = False,
        timeout: Optional[float] = None,
    ) -> Any:
        """
        Generuje odpowiedź czatu używając g4f z automatycznym fallback do innych modeli.
        
        Jeśli główny model nie działa, automatycznie próbuje modele zapasowe w kolejności.
        
        Args:
            messages: Lista słowników wiadomości z 'role' i 'content'
            model: Nazwa modelu (domyślnie skonfigurowany)
            stream: Czy streamować odpowiedzi
            timeout: Timeout żądania w sekundach (domyślnie skonfigurowany)
            
        Returns:
            Jeśli stream=False: Tekst odpowiedzi
            Jeśli stream=True: AsyncIterator chunków odpowiedzi
            
        Raises:
            AIUnavailableError: Jeśli serwis wyłączony lub wszystkie modele niedostępne
            AIValidationError: Jeśli walidacja wejścia nie powiodła się
            AITimeoutError: Jeśli żądanie przekroczy limit czasu
            AIRateLimitError: Jeśli przekroczono limit żądań
        """
        if not self.enabled or not self.client:
            raise AIUnavailableError("Serwis G4F jest wyłączony lub niedostępny")
        
        sanitized_messages = self._validate_and_sanitize_prompt(messages)
        
        if not sanitized_messages:
            raise AIValidationError("Wymagana jest przynajmniej jedna wiadomość")
        
        primary_model = model or self.default_model
        timeout = timeout or self.default_timeout
        
        models_to_try = [primary_model]
        for fallback_model in self.fallback_models:
            if fallback_model not in models_to_try:
                models_to_try.append(fallback_model)
        
        logger.info(f"Generowanie odpowiedzi czatu: modele={models_to_try}, wiadomości={len(sanitized_messages)}, stream={stream}")
        
        last_error = None
        for model_to_try in models_to_try:
            try:
                logger.info(f"Próba użycia modelu: {model_to_try}")
                
                if stream:
                    try:
                        response = await asyncio.wait_for(
                            self.client.chat.completions.create(
                                model=model_to_try,
                                messages=sanitized_messages,
                                stream=True,
                                web_search=False,
                            ),
                            timeout=timeout
                        )
                        logger.info(f"Pomyślnie użyto modelu: {model_to_try} (streaming)")
                        return response
                    except asyncio.TimeoutError:
                        raise AITimeoutError(f"Żądanie streamingu przekroczyło limit czasu po {timeout}s")
                    except Exception as e:
                        error_msg = str(e).lower()
                        if 'airforce' in error_msg or 'discord.gg' in error_msg or 'model does not exist' in error_msg:
                            logger.warning(f"Zablokowano spam providera AirForce: {str(e)}")
                            raise AIUnavailableError(f"Provider zablokowany: {str(e)}")
                        if any(term in error_msg for term in ['rate limit', 'too many requests', '429']):
                            raise AIRateLimitError(f"Przekroczono limit żądań: {str(e)}")
                        if any(term in error_msg for term in ['provider', 'unavailable', '503', '502']):
                            raise AIUnavailableError(f"Provider AI niedostępny: {str(e)}")
                        raise AIUnavailableError(f"Żądanie streamingu nie powiodło się: {str(e)}")
                else:
                    async def _generate():
                        try:
                            response = await self.client.chat.completions.create(
                                model=model_to_try,
                                messages=sanitized_messages,
                                web_search=False,
                            )
                            content = None
                            if hasattr(response, 'choices') and response.choices:
                                if hasattr(response.choices[0], 'message'):
                                    content = response.choices[0].message.content
                            if not content and hasattr(response, 'content'):
                                content = response.content
                            if not content:
                                content = str(response) if response else ""
                            
                            if content:
                                content_lower = content.lower()
                                if 'discord.gg' in content_lower or 'airforce' in content_lower or 'model does not exist' in content_lower:
                                    logger.warning(f"Zablokowano spam AirForce w treści odpowiedzi dla modelu {model_to_try}")
                                    raise AIUnavailableError("Provider zablokowany: wykryto spam AirForce w odpowiedzi")
                            
                            return content if content else ""
                        except Exception as e:
                            if isinstance(e, (AIUnavailableError, AITimeoutError, AIRateLimitError, AIValidationError)):
                                raise
                            error_msg = str(e).lower()
                            if 'airforce' in error_msg or 'discord.gg' in error_msg or 'model does not exist' in error_msg:
                                logger.warning(f"Zablokowano spam providera AirForce dla modelu {model_to_try}: {str(e)}")
                                raise AIUnavailableError(f"Provider zablokowany: {str(e)}")
                            logger.error(f"Żądanie G4F nie powiodło się dla modelu {model_to_try}: {error_msg}", exc_info=True)
                            raise AIUnavailableError(f"Żądanie G4F nie powiodło się: {error_msg}")
                    
                    result = await self._execute_with_retry(
                        _generate(),
                        timeout=timeout,
                        operation_name=f"Uzupełnienie czatu (model: {model_to_try})"
                    )
                    logger.info(f"Pomyślnie użyto modelu: {model_to_try}")
                    return result
                    
            except (AIUnavailableError, AITimeoutError) as e:
                last_error = e
                logger.warning(f"Model {model_to_try} niedostępny: {str(e)}, próba następnego modelu...")
                continue
            except AIRateLimitError as e:
                last_error = e
                logger.warning(f"Model {model_to_try} z limitem żądań: {str(e)}, próba następnego modelu...")
                continue
            except AIValidationError as e:
                raise
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model_to_try} nie powiódł się z nieoczekiwanym błędem: {str(e)}, próba następnego modelu...")
                continue
        
        logger.error(f"Wszystkie modele nie powiodły się: {models_to_try}")
        if last_error:
            raise last_error
        raise AIUnavailableError(f"Wszystkie modele niedostępne: {', '.join(models_to_try)}")
    
    async def stream_chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> AsyncIterator[str]:
        """
        Streamuje chunki odpowiedzi czatu.
        
        Args:
            messages: Lista słowników wiadomości
            model: Nazwa modelu
            timeout: Timeout żądania
            
        Yields:
            Chunki tekstu odpowiedzi
            
        Raises:
            AIUnavailableError: Jeśli serwis wyłączony lub niedostępny
            AIValidationError: Jeśli walidacja wejścia nie powiodła się
            AITimeoutError: Jeśli żądanie przekroczy limit czasu
            AIRateLimitError: Jeśli przekroczono limit żądań
        """
        response = await self.generate_chat(
            messages=messages,
            model=model,
            stream=True,
            timeout=timeout,
        )
        
        try:
            buffer = ""
            async for chunk in response:
                chunk_content = None
                if hasattr(chunk, 'choices') and chunk.choices:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        chunk_content = delta.content
                elif hasattr(chunk, 'content') and chunk.content:
                    chunk_content = chunk.content
                
                if chunk_content:
                    buffer += chunk_content
                    check_buffer = buffer[-200:].lower()
                    if 'discord.gg' in check_buffer or ('airforce' in check_buffer and 'model does not exist' in check_buffer):
                        logger.warning("Wykryto spam AirForce w odpowiedzi streamingu")
                        raise AIUnavailableError("Provider zablokowany: wykryto spam AirForce w odpowiedzi")
                    
                    yield chunk_content
        except Exception as e:
            if isinstance(e, (AIUnavailableError, AITimeoutError, AIRateLimitError, AIValidationError)):
                raise
            logger.error(f"Streaming nie powiódł się: {str(e)}", exc_info=True)
            raise AIUnavailableError(f"Streaming nie powiódł się: {str(e)}")


_service_instance: Optional[G4FService] = None


def get_g4f_service() -> G4FService:
    """
    Pobiera lub tworzy globalną instancję serwisu G4F.
    
    Returns:
        Instancja G4FService
    """
    global _service_instance
    if _service_instance is None:
        from config import settings
        _service_instance = G4FService(
            enabled=getattr(settings, 'G4F_ENABLED', True),
            default_model=getattr(settings, 'G4F_DEFAULT_MODEL', DEFAULT_MODEL),
            default_timeout=getattr(settings, 'G4F_TIMEOUT', DEFAULT_TIMEOUT),
            fallback_models=getattr(settings, 'G4F_FALLBACK_MODELS', []),
            blocked_providers=getattr(settings, 'G4F_BLOCKED_PROVIDERS', []),
        )
    return _service_instance

