"""
Функции-хелперы для работы обработчиков.
Функции обработки данных
"""

import logging
import random
from datetime import datetime, timezone

from asgiref.sync import sync_to_async
from telegram import (
    CallbackQuery,
    Message,
)
from telegram.ext import CallbackContext

from bot.models import Question, UserSettings

logger = logging.getLogger(__name__)

TOPIC_MAPPING = {
    'func': 'Функции',
    'expressions': 'Выражения',
}


async def daily_task(context: CallbackContext) -> None:
    """
    Ежедневная задача, отправляющая напоминание пользователям
    с включенными уведомлениями.
    """

    logger.info('Запуск daily_task')

    users_with_notifications = await sync_to_async(
        lambda: list(
            UserSettings.objects.filter(notification=True)
            .select_related('user')
        )
    )()

    for settings in users_with_notifications:
        user = settings.user
        notification_time = settings.notification_time

        now_utc = datetime.now(timezone.utc).time()
        if (
            now_utc.hour == notification_time.hour
            and now_utc.minute == notification_time.minute
        ):
            try:
                await context.bot.send_message(
                    chat_id=user.user_id,
                    text='Не забудь повторить теорию!'
                )
                logger.info(
                    f'Уведомление отправлено пользователю {user.user_id}.'
                )
            except Exception as e:
                logger.error(
                    'Ошибка при отправке уведомления'
                    f' пользователю {user.user_id}: {e}'
                )


@sync_to_async
def get_random_questions(queryset, count: int) -> list:
    """Получение случайных вопросов из QuerySet."""

    logger.info(f'Получение {count} случайных вопросов из QuerySet.')

    ids = list(queryset.values_list('id', flat=True))
    selected_ids = random.sample(ids, min(count, len(ids)))
    return list(queryset.filter(id__in=selected_ids))


@sync_to_async
def get_all_names_except(excluded_ids: list | int) -> list:
    """Получение всех значений поля name, исключая переданные id."""

    logger.info('Получение всех значений поля name, исключая переданные id.')

    # Преобразуем одиночное значение в список
    if isinstance(excluded_ids, int):
        excluded_ids = [excluded_ids]

    if not isinstance(excluded_ids, (list, int)):
        raise ValueError('excluded_ids должен быть int или list[int]')

    return list(
        Question.objects.exclude(
            id__in=excluded_ids).values_list('name', flat=True)
    )


async def get_chosen_topic(query: CallbackQuery) -> str | None:
    """Определяет выбранную тему по query.data."""

    logger.info('Определение выбранной темы по query.data.')

    if query.data is None:
        logger.error('Данные callback_query отсутствуют (query.data is None).')
        return None
    return TOPIC_MAPPING.get(query.data)


async def send_response_message(
        query: CallbackQuery, text: str, reply_markup=None) -> None:
    """Отправляет сообщение пользователю."""

    logger.info('Отправка сообщения пользователю.')

    if query and isinstance(query.message, Message):
        await query.message.reply_text(text, reply_markup=reply_markup)
    else:
        logger.error('Объект message отсутствует или имеет неправильный тип.')
