import os
from typing import List
from models.chat import ChatMessage, MessageRole
import logging

logger = logging.getLogger(__name__)

async def generate_ai_response(user_message: str, topic_name: str, project_name: str, chat_history: List[ChatMessage]) -> str:
    """Generate AI response using context"""
    
    system_prompt = f"""Ты ИИ-помощник в приложении FocusFlow. 
Пользователь изучает тему: "{topic_name}" 
в рамках проекта: "{project_name}".

Твоя задача:
- Давать краткие, понятные объяснения
- Не отвлекать от учебы
- Мотивировать продолжать сессию
- Отвечать на русском языке

Пользователь застрял и нуждается в помощи."""

    # TODO: Integrate with OpenAI/Gemini API
    # For now, return a placeholder response
    logger.info(f"AI request for topic: {topic_name}, message: {user_message}")
    
    return f"Я помогу тебе разобраться с темой '{topic_name}'. Что именно вызывает затруднения?"