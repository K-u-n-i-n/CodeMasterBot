import logging
import random

from telegram import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes
from typing import List

from bot.handlers import utils


logger = logging.getLogger(__name__)


async def get_incorrect_answers(
        current_question, all_names: List[str], num_answers: int) -> List[str]:
    """Возвращает случайные неправильные ответы для текущего вопроса."""

    return random.sample(all_names, k=min(num_answers, len(all_names)))


async def create_keyboard(options: List[str]) -> InlineKeyboardMarkup:
    """Создает клавиатуру для выбора ответа."""

    return InlineKeyboardMarkup([
        [InlineKeyboardButton(
            option, callback_data=option)] for option in options
    ] + [
        [InlineKeyboardButton('⛔ Завершить викторину ⛔', callback_data='end')]
    ])


async def send_question_message(
    update: Update, current_question,
        remaining_questions: int,
        keyboard: InlineKeyboardMarkup
) -> None:
    """Отправляет сообщение с вопросом и вариантами ответа."""

    message = update.message or (
        update.callback_query.message if update.callback_query else None)

    if isinstance(message, Message):
        await message.reply_text(
            text=(
                f'Осталось вопросов: {remaining_questions}\n\n'
                'Описание функции:\n\n'
                f'{current_question.description}\n\n'
                'Выберите правильный ответ:'
            ),
            reply_markup=keyboard,
        )


async def ask_next_question(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводит вопрос с вариантами ответа."""

    if context.user_data is None:
        return None

    current_question = context.user_data.get('current_question')

    if not current_question:
        logger.warning('Попытка задать вопрос, но вопрос не найден.')
        if update.message:
            await update.message.reply_text(
                'Вопрос не найден. Викторина завершена.'
            )
        return

    all_names = await utils.get_all_names_except(current_question.id)
    num_incorrect_answers = min(3, len(all_names))

    if num_incorrect_answers < 3:
        logger.warning(
            'Недостаточно неправильных вариантов'
            f' для вопроса {current_question.id}.'
        )

    # Получаем неправильные ответы
    incorrect_answers = await get_incorrect_answers(
        current_question, all_names, num_incorrect_answers
    )

    # Собираем все ответы (правильный + неправильные)
    options = [current_question.name] + incorrect_answers
    random.shuffle(options)

    keyboard = await create_keyboard(options)
    remaining_questions = len(context.user_data.get('quiz_questions', []))

    await send_question_message(
        update, current_question, remaining_questions, keyboard
    )
