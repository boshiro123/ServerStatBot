"""
Вспомогательные функции
"""
import os
import logging
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.metrics import UserSettings

logger = logging.getLogger(__name__)


async def get_or_create_user_settings(
    session: AsyncSession,
    user_id: int,
    username: Optional[str] = None
) -> UserSettings:
    """Получение или создание настроек пользователя"""
    try:
        stmt = select(UserSettings).where(UserSettings.user_id == user_id)
        result = await session.execute(stmt)
        user_settings = result.scalar_one_or_none()
        
        if not user_settings:
            user_settings = UserSettings(
                user_id=user_id,
                username=username,
            )
            session.add(user_settings)
            try:
                await session.commit()
                await session.refresh(user_settings)
                logger.info(f"Создан новый пользователь: {user_id}")
            except Exception as commit_error:
                # Возможно, пользователь был создан в другой сессии
                await session.rollback()
                result = await session.execute(stmt)
                user_settings = result.scalar_one_or_none()
                if not user_settings:
                    raise commit_error
        
        return user_settings
    except Exception as e:
        logger.error(f"Ошибка при получении настроек пользователя: {e}")
        await session.rollback()
        raise


def get_env_int(key: str, default: int) -> int:
    """Получение переменной окружения как int"""
    try:
        return int(os.getenv(key, default))
    except (ValueError, TypeError):
        return default


def get_env_float(key: str, default: float) -> float:
    """Получение переменной окружения как float"""
    try:
        return float(os.getenv(key, default))
    except (ValueError, TypeError):
        return default

