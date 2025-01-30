"""Функции работы с БД"""

import logging

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from bot.models import CustomUser, Tag, UserSettings


logger = logging.getLogger(__name__)


async def get_user_from_db(user_id: int) -> CustomUser | None:
    """Получает пользователя из базы данных."""

    try:
        return await sync_to_async(CustomUser.objects.get)(user_id=user_id)
    except ObjectDoesNotExist:
        logger.warning(f'Пользователь с id {user_id} не найден.')
        return None
    except Exception as e:
        logger.error(f'Ошибка при получении пользователя: {e}')
        return None


async def get_or_create_user_settings(user: CustomUser) -> UserSettings:
    """Получает или создаёт объект UserSettings для пользователя."""

    settings, created = await sync_to_async(UserSettings.objects.get_or_create)(user=user)
    if created:
        logger.info(
            f'Создан новый объект UserSettings для пользователя {user.id}.')
    return settings


async def update_user_topic(settings: UserSettings, tag_name: str) -> bool:
    """Обновляет тему в настройках пользователя."""

    try:
        tag = await sync_to_async(Tag.objects.get)(name=tag_name)
        settings.tag = tag
        await sync_to_async(settings.save)()
        return True
    except ObjectDoesNotExist:
        logger.error(f'Тема "{tag_name}" отсутствует в базе данных.')
        return False
