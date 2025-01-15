"""
Функции-хелперы для работы обработчиков.
"""

import logging
import os
import random

from asgiref.sync import sync_to_async
from telegram.ext import CallbackContext

from bot.models import Question


async def daily_task(context: CallbackContext) -> None:
    logging.info('Запуск daily_task')
    chat_id = os.getenv('BOOS_CHAT_ID')
    await context.bot.send_message(
        chat_id=chat_id, text='Не забудь повторить теорию!'
    )


@sync_to_async
def get_random_questions(queryset, count: int) -> list:
    """
    Получение случайных вопросов из QuerySet.
    """
    ids = list(queryset.values_list('id', flat=True))
    selected_ids = random.sample(ids, min(count, len(ids)))
    return list(queryset.filter(id__in=selected_ids))


@sync_to_async
def get_all_names_except(excluded_ids: list | int) -> list:
    """
    Получение всех значений поля name, исключая переданные id.
    """
    # Преобразуем одиночное значение в список
    if isinstance(excluded_ids, int):
        excluded_ids = [excluded_ids]

    if not isinstance(excluded_ids, (list, int)):
        raise ValueError('excluded_ids должен быть int или list[int]')

    return list(
        Question.objects.exclude(
            id__in=excluded_ids).values_list('name', flat=True)
    )


# async def gif_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик кнопки 'GIF'"""

#     if update.callback_query is None:
#         return

#     query = update.callback_query
#     await query.answer()  # Закрываем 'часики' у кнопки

#     # Отправляем GIF
#     await context.bot.send_animation(
#         chat_id=query.message.chat_id,
#         animation='https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif'
#     )


# async def sticker_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     """Обработчик кнопки 'Стикер'"""

#     if update.callback_query is None:
#         return

#     query = update.callback_query
#     await query.answer()  # Закрываем 'часики' у кнопки

#     # Отправляем стикер
#     await context.bot.send_sticker(
#         chat_id=query.message.chat_id,
#         sticker='CAACAgIAAxkBAAENI65nOalFB9bRBZR2EjqfzGEAATkDHaAAAgEAA8A2TxMYLnMwqz8tUTYE'
#     )
