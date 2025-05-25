"""Функции работы с БД"""

import logging
from typing import List, Tuple, Union

from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist

from bot.handlers import utils
from bot.models import CustomUser, Question, Tag, UserSettings

logger = logging.getLogger(__name__)

DEFAULT_SETTINGS_USER = {
    'tag': 'func',
    'difficulty': 'easy',
}


async def get_user_from_db(user_id: int) -> CustomUser | None:
    """Получает пользователя из базы данных."""

    logger.info(f'Получение пользователя с id {user_id} из бд.')

    try:
        return await sync_to_async(CustomUser.objects.get)(user_id=user_id)
    except ObjectDoesNotExist:
        logger.warning(f'Пользователь с id {user_id} в бд не найден.')
        return None
    except Exception as e:
        logger.error(f'Ошибка при получении пользователя: {e}')
        return None


async def get_or_create_user_settings(user: CustomUser) -> UserSettings:
    """Получает или создаёт объект UserSettings для пользователя."""

    logger.info(
        f'Получение или создание настроек пользователя {user.id} из бд.'
    )

    settings, created = await sync_to_async(
        UserSettings.objects.get_or_create
    )(user=user)
    if created:
        logger.info(
            f'Создан новый объект UserSettings для пользователя {user.id}.'
        )
    return settings


async def update_user_topic(settings: UserSettings, tag_name: str) -> bool:
    """Обновляет тему в настройках пользователя."""

    logger.info(
        f'Обновление темы в настройках пользователя {settings.user.id}.'
    )

    try:
        tag = await sync_to_async(Tag.objects.get)(name=tag_name)
        settings.tag = tag
        await sync_to_async(settings.save)()
        return True
    except ObjectDoesNotExist:
        logger.error(f'Тема "{tag_name}" отсутствует в базе данных.')
        return False


async def get_user_settings(
    user_id: int,
) -> Tuple[Union[UserSettings, dict], bool]:
    """
    Возвращает настройки пользователя.
    Если пользователя нет в БД или в UserSettings,
    возвращает глобальные настройки.
    """

    logger.info(f'Получение настроек пользователя с ID {user_id} из БД')

    try:
        user = await CustomUser.objects.aget(user_id=user_id)
        logger.info(f'Пользователь найден: {user.user_id}')

    except CustomUser.DoesNotExist:
        logger.warning(f'Пользователь с ID {user_id} не найден')
        return DEFAULT_SETTINGS_USER, False

    try:
        settings = await UserSettings.objects.select_related('tag').aget(
            user=user
        )
        logger.info(f'Настройки для пользователя с ID {user_id} найдены')
        return settings, True

    except UserSettings.DoesNotExist:
        logger.info(f'Настройки для пользователя с ID {user_id} не найдены')
        return DEFAULT_SETTINGS_USER, False


async def get_random_questions_by_tag(
    count: int, tag_slug: str
) -> List[Question]:
    """Получает случайные вопросы по указанному тегу."""

    logger.info(f'Получение случайных вопросов по тегу {tag_slug}.')

    queryset = Question.objects.filter(tags__slug=tag_slug)
    return await utils.get_random_questions(queryset, count)
