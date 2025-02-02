import logging

from telegram import Update, Message
from typing import Optional, cast

logger = logging.getLogger(__name__)


def get_safe_message(update: Update) -> Optional[Message]:
    """
    Возвращает объект Message из update.
    Если update.message отсутствует,
    пытается вернуть update.callback_query.message.
    """

    if update.message:
        return update.message
    elif update.callback_query and update.callback_query.message:
        return cast(Message, update.callback_query.message)
    else:
        logger.error("Не удалось получить сообщение из update.")
        return None


async def send_message(update: Update, text: str) -> None:
    """
    Отправляет сообщение с заданным текстом,
    используя безопасное извлечение объекта Message.
    """

    message = get_safe_message(update)
    if message:
        await message.reply_text(text)
    else:
        logger.error(
            'Отправка сообщения не выполнена,'
            ' так как объект Message отсутствует.'
        )


async def send_no_questions_message(update: Update) -> None:
    """Отправляет сообщение о том, что вопросов нет."""

    await send_message(
        update,
        'К сожалению, в этой теме вопросов нет. 😔\n'
        'Выберите пожалуйста другую тему'
    )


async def send_error_message(update: Update) -> None:
    """Отправляет сообщение об ошибке."""

    await send_message(
        update,
        'Что-то пошло не так. Вопросы отсутствуют.'
    )
