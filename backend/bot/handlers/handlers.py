"""
Головной модуль-обработчик всех пользовательских событий,
которые могут возникнуть у пользователей в процессе взаимодействия с ботом.
"""

import random
import logging

from asgiref.sync import sync_to_async
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from bot.handlers.utils import get_all_names_except, get_random_questions
from bot.models import CustomUser, Question, UserSettings
from .keyboards import (
    config_keyboard,
    complexity_keyboard,
    topic_keyboard,
    notification_keyboard
)

DEFAULT_SETTINGS_USER = {
    'tag': 'func',
    'difficulty': 'easy',
}


async def handle_config(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает настройку бота"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите параметр для настройки:',
            reply_markup=config_keyboard
        )


async def handle_complexity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор сложности"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите сложность:', reply_markup=complexity_keyboard
        )


async def handle_topic_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор темы"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите тему:', reply_markup=topic_keyboard
        )


async def handle_notifications_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запросы, связанные с изменением настроек оповещений"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите параметр для настройки:',
            reply_markup=notification_keyboard
        )


def get_next_question(context):
    """Получает вопрос, удаляет его из списка и возвращает оставшееся количество вопросов."""
    questions = context.user_data.get('quiz_questions', [])
    if questions:
        next_question = questions.pop(0)
        context.user_data['quiz_questions'] = questions
        return next_question
    return None


async def get_user_settings(user_id: int) -> tuple[dict, bool]:
    """
    Возвращает настройки пользователя.
    Если пользователя нет в БД, возвращает глобальные настройки.
    Если пользователя нет в UserSettings, возвращает его, но с флагом отсутствия настроек.
    """
    try:
        user = await CustomUser.objects.aget(id=user_id)
    except CustomUser.DoesNotExist:
        return DEFAULT_SETTINGS_USER, False

    try:
        settings = await user.settings.aget()
        return settings, True
    except UserSettings.DoesNotExist:
        return DEFAULT_SETTINGS_USER, False


async def handle_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало викторины."""
    if not update.message:
        return

    user_id = update.effective_user.id

    user_settings, has_personal_settings = await get_user_settings(user_id)

    if not has_personal_settings:
        await update.message.reply_text(
            '❗ Вы можете настроить бота для себя! ❗\n'
            '✨ Используйте кнопку "Настроить бота". ✨'
        )

    tag_slug = user_settings['tag'] or DEFAULT_SETTINGS_USER['tag']

    random_questions = await get_random_questions_by_tag(10, tag_slug=tag_slug)
    if not random_questions:
        await send_no_questions_message(update)
        return

    await prepare_quiz_context(context, random_questions)

    next_question = await get_next_question_from_context(context)
    if not next_question:
        await send_error_message(update)
        return

    await ask_next_question(update, context)


async def get_random_questions_by_tag(count: int, tag_slug: str):
    """Получает случайные вопросы по указанному тегу."""
    queryset = Question.objects.filter(tags__slug=tag_slug)
    return await get_random_questions(queryset, count)


async def send_no_questions_message(update: Update):
    """Отправляет сообщение о том, что вопросов нет."""
    await update.message.reply_text('К сожалению, вопросов нет.')


async def prepare_quiz_context(context: ContextTypes.DEFAULT_TYPE, questions: list[Question]):
    """Сохраняет данные викторины в user_data."""
    context.user_data['quiz_questions'] = questions
    context.user_data['used_names'] = [q.name for q in questions]


async def get_next_question_from_context(context: ContextTypes.DEFAULT_TYPE):
    """Извлекает следующий вопрос из контекста."""
    next_question = get_next_question(context)
    if next_question:
        context.user_data['current_question'] = next_question
    return next_question


async def send_error_message(update: Update):
    """Отправляет сообщение об ошибке."""
    await update.message.reply_text('Что-то пошло не так. Вопросы отсутствуют.')


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод вопроса с вариантами ответа."""

    current_question = context.user_data.get('current_question')
    if not current_question:
        logging.warning('Попытка задать вопрос, но вопрос не найден.')
        return

    all_names = await get_all_names_except(current_question.id)
    incorrect_answers = random.sample(all_names, k=min(3, len(all_names)))
    options = [current_question.name] + incorrect_answers
    random.shuffle(options)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(option, callback_data=option)] for option in options
    ] + [
        [InlineKeyboardButton('⛔ Завершить викторину ⛔', callback_data='end')]
    ])

    remaining_questions = len(context.user_data.get('quiz_questions', []))

    message = update.message or update.callback_query.message
    if message:
        await message.reply_text(
            text=(
                f'Осталось вопросов: {remaining_questions}\n\n'
                f'Описание функции:\n\n'
                f'{current_question.description}\n\n'
                f'Выберите правильный ответ:'
            ),
            reply_markup=keyboard,
        )


async def handle_question_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа пользователя на текущий вопрос."""
    query = update.callback_query
    await query.answer()

    current_question = context.user_data.get('current_question')
    if not current_question:
        await query.edit_message_text('Вопрос не найден.')
        return

    user_answer = query.data  # Ответ пользователя из callback_data

    if user_answer == current_question.name:
        text = (
            f'✅ Правильно! Отличная работа!\n\n'
            f'Название функции: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )
    else:
        text = (
            f'❌ Неправильно.\n\n'
            f'Ваш ответ: {user_answer}\n'
            f'Правильный ответ: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )

    await query.edit_message_text(text)

    await handle_next_step(update, context)


async def handle_next_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Определяет следующий шаг: завершение викторины или показ следующего вопроса."""
    next_question = get_next_question(context)

    if next_question:
        # Если остались вопросы, задаем следующий
        context.user_data['current_question'] = next_question
        await ask_next_question(update, context)
    else:
        await (update.message or update.callback_query.message).reply_text('Викторина завершена. Спасибо за участие! 👋')
        context.user_data.clear()


async def handle_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопки 'Завершить викторину'."""

    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    await query.edit_message_text('⛔ Викторина завершена! ⛔')


async def handle_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает регистрацию пользователя"""

    logging.info('Запуск handle_registration')

    if not update.callback_query:
        logging.warning('Обновление не содержит callback_query.')
        return

    callback_data = update.callback_query.data

    if callback_data != 'registration':
        logging.warning(f'Неожиданный callback_data: {callback_data}')
        return

    await update.callback_query.answer()

    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user, created = await sync_to_async(
        CustomUser.objects.get_or_create)(user_id=telegram_id)

    if created:
        user.username = username
        await sync_to_async(user.save)()
        await update.callback_query.message.reply_text('Вы зарегистрированы!')
    else:
        await update.callback_query.message.reply_text(
            f'{user.username} вы уже зарегистрированы'
        )


async def handle_generic_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает универсальный callback-запрос"""

    if update.callback_query is None:
        return

    query = update.callback_query

    await query.answer()
    await query.edit_message_text(
        text='Эта функция в данный момент не реализована.'
    )
