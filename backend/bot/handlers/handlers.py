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
from bot.models import CustomUser, Question
from .keyboards import (
    config_keyboard,
    complexity_keyboard,
    topic_keyboard,
    next_keyboard,
    notification_keyboard
)


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


async def handle_help_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает запрос информации о боте"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Тут будет подробная информация о боте.'
        )


async def handle_quiz_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Начало викторины."""
    if update.message:
        queryset = Question.objects.filter(tags__slug='func')
        random_questions = await get_random_questions(queryset, 10)

        if not random_questions:
            await update.message.reply_text('К сожалению, вопросов нет.')
            return

        context.user_data['quiz_questions'] = random_questions
        context.user_data['current_question'] = None
        context.user_data['used_names'] = [q.name for q in random_questions]

        await ask_next_question(update, context)


async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод следующего вопроса с вариантами ответа."""

    logging.info('Начинаем задавать следующий вопрос')
    questions = context.user_data.get('quiz_questions', [])
    logging.info(f'Осталось вопросов: {len(questions)}')

    if not questions:
        message = update.message or update.callback_query.message
        if message:
            await message.reply_text('💥 Викторина завершена!')
            # Здесь нужно реализовать функцию подсчета правильных ответов
        context.user_data.clear()
        return

    # Берем текущий вопрос
    current_question = questions.pop(0)
    context.user_data['current_question'] = current_question
    context.user_data['quiz_questions'] = questions
    logging.info(f'Текущий вопрос: {current_question.description}')

    # Получаем случайные варианты ответа
    all_names = await get_all_names_except(current_question.id)
    logging.info(f'Всего доступных имен для ответа: {len(all_names)}')
    incorrect_answers = random.sample(all_names, k=min(3, len(all_names)))
    options = [current_question.name] + incorrect_answers
    random.shuffle(options)

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(option, callback_data=option)] for option in options
    ])
    logging.info('Клавиатура сформирована')

    message = update.message or update.callback_query.message
    if message:
        await message.reply_text(
            text=(
                f'Описание функции:\n\n'
                f'{current_question.description}\n\nВыберите правильный ответ:'
            ),
            reply_markup=keyboard,
        )
        logging.info('Вопрос отправлен пользователю.')
    else:
        logging.warning('Вопрос не отправлен.')


async def handle_question_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ответа пользователя на текущий вопрос."""

    query = update.callback_query
    await query.answer()

    current_question = context.user_data.get('current_question')
    if not current_question:
        await query.edit_message_text('Вопрос не найден.')
        return

    user_answer = query.data  # Ответ пользователя из callback_data
    questions = context.user_data.get('quiz_questions', [])

    # Проверяем, правильный ли ответ
    if user_answer == current_question.name:
        text = (
            f'✅ Правильно! Отличная работа!\n\n'
            f'Осталось вопросов: {len(questions)}\n\n'
            f'Название функции: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )
    else:
        text = (
            f'❌ Неправильно.\n\n'
            f'Осталось вопросов: {len(questions)}\n\n'
            f'Ваш ответ: {user_answer}\n'
            f'Правильный ответ: {current_question.name}\n\n'
            f'Описание функции:\n{current_question.description}\n\n'
            f'Синтаксис:\n{current_question.syntax}'
        )

    await query.edit_message_text(text)

    await query.message.reply_text(
        text='Что вы хотите сделать дальше?',
        reply_markup=next_keyboard,
    )


async def handle_next_or_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок 'Далее' и 'Завершить викторину'."""

    query = update.callback_query
    await query.answer()

    if query.data == 'next':
        await ask_next_question(update, context)
        await query.edit_message_text('🔥 Следующий вопрос:')

    elif query.data == 'end':
        context.user_data.clear()
        await query.edit_message_text(
            'Викторина завершена. Спасибо за участие! 👋'
        )


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
