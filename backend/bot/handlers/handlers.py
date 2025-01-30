"""
Головной модуль-обработчик всех пользовательских событий,
которые могут возникнуть у пользователей в процессе взаимодействия с ботом.
"""

import random
import logging
from typing import Tuple, List, Union

from asgiref.sync import sync_to_async
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ContextTypes

from bot.handlers import db_helpers, context_helpers, utils
from bot.models import CustomUser, Question, UserSettings
from .keyboards import (
    config_keyboard,
    complexity_keyboard,
    menu_keyboard,
    notification_keyboard,
    topic_keyboard,
)


logger = logging.getLogger(__name__)

DEFAULT_SETTINGS_USER = {
    'tag': 'func',
    'difficulty': 'easy',
}


async def handle_config(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает настройку бота"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите параметр для настройки:',
            reply_markup=config_keyboard
        )


async def handle_complexity(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор сложности"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите сложность:', reply_markup=complexity_keyboard
        )


async def handle_topic_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор темы"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите тему:', reply_markup=topic_keyboard
        )


async def handle_topic_choice(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор темы викторины и сохраняет её в настройках."""

    query = update.callback_query
    if not query:
        logger.warning('CallbackQuery отсутствует в update.')
        return

    await query.answer()
    tg_user = query.from_user

    user = await db_helpers.get_user_from_db(tg_user.id)
    if not user:
        await utils.send_response_message(
            query, 'Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию.'
        )
        return

    chosen_topic = await utils.get_chosen_topic(query)
    if not chosen_topic:
        await utils.send_response_message(
            query, 'Выбранная тема не найдена. Попробуйте снова.'
        )
        return

    settings = await db_helpers.get_or_create_user_settings(user)
    topic_updated = await db_helpers.update_user_topic(settings, chosen_topic)

    if not topic_updated:
        await utils.send_response_message(
            query, f'Тема "{chosen_topic}" отсутствует в базе данных.'
        )
        return

    await utils.send_response_message(
        query,
        f'Тема викторины обновлена: {chosen_topic}.\n'
        'Выберите другие настройки или можете проходить викторину.',
        reply_markup=config_keyboard
    )


async def handle_notifications_settings(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает запросы, связанные с изменением настроек оповещений"""

    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(
            text='Выберите параметр для настройки:',
            reply_markup=notification_keyboard
        )


async def get_user_settings(
        user_id: int) -> Tuple[Union[UserSettings, dict], bool]:
    """
    Возвращает настройки пользователя.
    Если пользователя нет в БД или в UserSettings,
    возвращает глобальные настройки.
    """
    try:
        user = await CustomUser.objects.aget(user_id=user_id)
        logger.info(f'Пользователь найден: {user.user_id}')

    except CustomUser.DoesNotExist:
        logger.warning(f'Пользователь с ID {user_id} не найден')
        return DEFAULT_SETTINGS_USER, False

    try:
        settings = await UserSettings.objects.select_related('tag').aget(
            user=user)
        logger.info(f'Настройки для пользователя с ID {user_id} найдены')
        return settings, True

    except UserSettings.DoesNotExist:
        logger.info(f'Настройки для пользователя с ID {user_id} не найдены')
        return DEFAULT_SETTINGS_USER, False


async def handle_my_settings(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает кнопку 'Мои настройки'."""

    query = update.callback_query
    user_id = query.from_user.id
    settings, has_settings = await get_user_settings(user_id)
    keyboard = menu_keyboard

    if not has_settings:
        text = 'У вас пока нет сохраненных настроек.'
    else:
        text = (
            f'📌 <b>Ваши настройки</b>\n\n'
            f'🎯 <b>Тема:</b> {settings.tag or 'Не настроено'}\n'
            f'⚙️ <b>Сложность:</b> {settings.difficulty or 'Не настроено'}\n'
            f'🔔 <b>Оповещение:</b> {settings.notification or 'Не настроено'}\n'
            f'⏰ <b>Время оповещений:</b>'
            f'{settings.notification_time.strftime("%H:%M")}\n\n'
            f'📢❗🚨 <b>Внимание: время по UTC</b> 📢❗🚨'
        )

    await query.answer()
    await query.edit_message_text(
        text=text, reply_markup=keyboard, parse_mode='HTML'
    )


async def handle_quiz_start(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало викторины."""

    if not update.message:
        return

    user_id = update.effective_user.id
    user_settings, has_personal_settings = await get_user_settings(user_id)

    if not has_personal_settings:
        await update.message.reply_text(
            '❗ Вы можете настроить бота для себя!\n\n'
            'Используйте кнопку в меню:\n'
            '✨ "Настроить бота" ✨\n\n'
            'Для настройки бота необходимо:\n'
            '⚠️ "Зарегистрироваться" ⚠️'
        )
        tag_slug = DEFAULT_SETTINGS_USER['tag']

    else:
        tag_slug = user_settings.tag.slug

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


async def get_random_questions_by_tag(
        count: int, tag_slug: str) -> List[Question]:
    """Получает случайные вопросы по указанному тегу."""

    queryset = Question.objects.filter(tags__slug=tag_slug)
    return await utils.get_random_questions(queryset, count)


async def send_no_questions_message(update: Update) -> None:
    """Отправляет сообщение о том, что вопросов нет."""

    await update.message.reply_text(
        'К сожалению, в этой теме вопросов нет. 😔\n'
        'Выберите пожалуйста другую тему'
    )


async def prepare_quiz_context(
        context: ContextTypes.DEFAULT_TYPE, questions: List[Question]) -> None:
    """Сохраняет данные викторины в user_data."""

    context.user_data['quiz_questions'] = questions
    context.user_data['used_names'] = [q.name for q in questions]


async def get_next_question_from_context(
        context: ContextTypes.DEFAULT_TYPE) -> Union[Question, None]:
    """Извлекает следующий вопрос из контекста."""

    next_question = context_helpers.get_next_question(context)
    if next_question:
        context.user_data['current_question'] = next_question
    return next_question


async def send_error_message(update: Update) -> None:
    """Отправляет сообщение об ошибке."""

    await update.message.reply_text('Что-то пошло не так. Вопросы отсутствуют.')


async def ask_next_question(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Вывод вопроса с вариантами ответа."""

    current_question = context.user_data.get('current_question')
    if not current_question:
        logger.warning('Попытка задать вопрос, но вопрос не найден.')
        return

    all_names = await utils.get_all_names_except(current_question.id)
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


async def handle_question_answer(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


async def handle_next_step(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Определяет следующий шаг: завершение викторины или показ следующего вопроса."""

    next_question = context_helpers.get_next_question(context)

    if next_question:
        context.user_data['current_question'] = next_question
        await ask_next_question(update, context)
    else:
        await (update.message or update.callback_query.message).reply_text(
            'Викторина завершена. Спасибо за участие! 👋'
        )
        context.user_data.clear()


async def handle_end(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Завершить викторину'."""

    query = update.callback_query
    await query.answer()

    context.user_data.clear()
    await query.edit_message_text('⛔ Викторина завершена! ⛔')


async def handle_registration(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает регистрацию пользователя"""

    logger.info('Запуск handle_registration')

    if not update.callback_query:
        logger.warning('Обновление не содержит callback_query.')
        return

    callback_data = update.callback_query.data

    if callback_data != 'registration':
        logger.warning(f'Неожиданный callback_data: {callback_data}')
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


async def handle_generic_callback(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает универсальный callback-запрос"""

    if update.callback_query is None:
        return

    query = update.callback_query

    await query.answer()
    await query.edit_message_text(
        text='Эта функция в данный момент не реализована.'
    )
