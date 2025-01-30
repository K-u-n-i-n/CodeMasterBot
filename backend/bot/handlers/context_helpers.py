"""Логика работы с контекстом"""

from typing import Union

from telegram.ext import ContextTypes

from bot.models import Question


def get_next_question(
        context: ContextTypes.DEFAULT_TYPE) -> Union[Question, None]:
    """
    Получает вопрос, удаляет его из списка и
    возвращает оставшееся количество вопросов.
    """

    questions = context.user_data.get('quiz_questions', [])
    if questions:
        next_question = questions.pop(0)
        context.user_data['quiz_questions'] = questions
        return next_question
    return None
