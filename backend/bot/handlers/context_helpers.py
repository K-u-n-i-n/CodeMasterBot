"""Логика работы с контекстом"""

import logging
from typing import Union, List, Optional

from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes

from bot.models import Question

logger = logging.getLogger(__name__)


def get_next_question(
        context: ContextTypes.DEFAULT_TYPE) -> Union[Question, None]:
    """
    Получает вопрос, удаляет его из списка и
    возвращает оставшееся количество вопросов.
    """

    if context.user_data is None:
        return None

    questions = context.user_data.get('quiz_questions', [])

    if questions:
        next_question = questions.pop(0)
        context.user_data['quiz_questions'] = questions
        return next_question
    return None


async def prepare_quiz_context(
        context: ContextTypes.DEFAULT_TYPE, questions: List[Question]) -> None:
    """Сохраняет данные викторины в user_data."""

    if context.user_data is None:
        return None

    context.user_data['quiz_questions'] = questions
    context.user_data['used_names'] = [q.name for q in questions]


async def get_next_question_from_context(
        context: ContextTypes.DEFAULT_TYPE) -> Union[Question, None]:
    """Извлекает следующий вопрос из контекста."""

    if context.user_data is None:
        return None

    next_question = get_next_question(context)
    if next_question:
        context.user_data['current_question'] = next_question
    return next_question


def get_callback_query(update: Update) -> Optional[CallbackQuery]:
    """Извлекает callback_query из update и логирует его отсутствие."""

    query = update.callback_query
    if query is None:
        logger.warning('Callback_query отсутствует в update.')
    return query
