import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import handlers

logger = logging.getLogger(__name__)


async def handle_text_answer(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Обрабатывает текстовый ответ, введённый пользователем в Hard режиме.
    Сравнение производится строго.
    """

    logger.info('Обработка текстового ответа.')

    if context.user_data is None:
        logger.warning('context.user_data отсутствует.')
        return

    if update.message is None:
        logger.warning('update.message отсутствует.')
        return

    current_question = context.user_data.get('current_question')
    if not current_question:
        await update.message.reply_text('Вопрос не найден.')
        return

    if update.message.text is None:
        logger.warning('update.message.text отсутствует.')
        return

    user_answer = update.message.text.strip()

    if user_answer == current_question.name:
        context.user_data['correct_answers'] = (
            context.user_data.get('correct_answers', 0) + 1
        )
        text = (
            '✅ Правильно! Отличная работа!\n\n'
            f'Название функции: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )
    else:
        text = (
            '❌ Неправильно.\n\n'
            f'Ваш ответ: {user_answer}\n'
            f'Правильный ответ: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )

    await update.message.reply_text(text)
    await handlers.handle_next_step(update, context)
