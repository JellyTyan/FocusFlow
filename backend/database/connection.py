from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from database.user_db import get_async_session, create_db_and_tables
import logging
import asyncio

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize database tables with retry logic"""
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # Create all tables (users, projects, topics, sessions, chat_messages, subjects, client_logs)
            await create_db_and_tables()
            logger.info("Database tables created successfully")
            return
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database initialization attempt {attempt + 1} failed: {e}. Retrying in {retry_delay} seconds...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error(f"Failed to initialize database after {max_retries} attempts: {e}", exc_info=True)
                raise

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session"""
    async for session in get_async_session():
        yield session
