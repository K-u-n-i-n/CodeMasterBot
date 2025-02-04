"""
Головной модуль-обработчик всех пользовательских событий,
которые могут возникнуть у пользователей в процессе взаимодействия с ботом.
"""

import logging

from asgiref.sync import sync_to_async
from telegram import Update, Message
from telegram.ext import ContextTypes

from bot.handlers import (
    db_helpers,
    context_helpers,
    messages,
    quiz_helpers,
    utils
)
from bot.models import CustomUser, UserSettings
from .keyboards import (
    config_keyboard,
    complexity_keyboard,
    notification_keyboard,
    topic_keyboard,
)

logger = logging.getLogger(__name__)


async def handle_config(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает настройку бота"""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    user_id = query.from_user.id
    settings, has_settings = await db_helpers.get_user_settings(user_id)
    keyboard = config_keyboard

    if not has_settings:
        text = 'У вас пока нет сохраненных настроек.'
    else:
        if isinstance(settings, UserSettings):
            text = (
                '📌 <b>Ваши настройки</b>\n\n'
                '⚙️ <b>Сложность:</b> '
                f'{settings.difficulty or 'Не настроено'}\n'
                '🎯 <b>Тема:</b> '
                f'{settings.tag or 'Не настроено'}\n'
                '🔔 <b>Оповещение:</b> '
                f'{'ВКЛ' if settings.notification else 'ВЫКЛ'}\n'
                '⏰ <b>Время оповещений:</b> '
                f'{settings.notification_time.strftime("%H:%M")}\n\n'
                '📢❗🚨 <b>Внимание: время по UTC</b> 📢❗🚨'
            )

    await query.answer()
    await query.edit_message_text(
        text=text, reply_markup=keyboard, parse_mode='HTML'
    )


async def handle_complexity(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор сложности"""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()
    await query.edit_message_text(
        text='Выберите сложность:', reply_markup=complexity_keyboard
    )


async def handle_topic_selection(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор темы"""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()
    await query.edit_message_text(
        text='Выберите тему:', reply_markup=topic_keyboard
    )


async def handle_topic_choice(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает выбор темы викторины и сохраняет её в настройках."""

    query = context_helpers.get_callback_query(update)
    if not query:
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
            query, 'Что-то пошло не так. Выбранная тема не найдена.'
        )
        return

    settings = await db_helpers.get_or_create_user_settings(user)
    topic_updated = await db_helpers.update_user_topic(settings, chosen_topic)

    if not topic_updated:
        await utils.send_response_message(
            query, f'Тема "{chosen_topic}" отсутствует в базе данных.'
        )
        return

    await handle_config(update, context)


async def handle_notifications_settings(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает запросы, связанные с изменением настроек оповещений"""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()
    await query.edit_message_text(
        text='Выберите параметр для настройки:',
        reply_markup=notification_keyboard
    )


async def handle_quiz_start(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Начало викторины."""

    logger.info('Начало обработки запроса "Викторина".')

    if not update.message:
        logger.error('Обновление не содержит сообщения.')
        return

    if update.effective_user is None:
        logger.warning('effective_user отсутствует в update.')
        await update.message.reply_text('Не удалось определить пользователя.')
        return

    user_id = update.effective_user.id
    user_settings, has_personal_settings = (
        await db_helpers.get_user_settings(user_id)
    )

    if not has_personal_settings:
        await update.message.reply_text(
            '❗ Вы можете настроить бота для себя!\n\n'
            'Используйте кнопку в меню:\n'
            '✨ "Настроить бота" ✨\n\n'
            'Для настройки бота необходимо:\n'
            '⚠️ "Зарегистрироваться" ⚠️'
        )
        tag_slug = db_helpers.DEFAULT_SETTINGS_USER['tag']

    else:
        if isinstance(user_settings, UserSettings):
            tag_slug = user_settings.tag.slug
        else:
            logger.warning(
                f'Настройки пользователя с ID {user_id}'
                f' некорректны: {user_settings}'
            )
            await update.message.reply_text('Ошибка при получении настроек.')
            tag_slug = db_helpers.DEFAULT_SETTINGS_USER['tag']

    random_questions = await db_helpers.get_random_questions_by_tag(
        10, tag_slug=tag_slug)
    if not random_questions:
        await messages.send_no_questions_message(update)
        return

    await context_helpers.prepare_quiz_context(context, random_questions)

    next_question = await context_helpers.get_next_question_from_context(
        context)
    if not next_question:
        await messages.send_error_message(update)
        return

    await quiz_helpers.ask_next_question(update, context)


async def handle_question_answer(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка ответа пользователя на текущий вопрос."""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()

    if context.user_data is None:
        logger.warning('context.user_data отсутствует.')
        await query.edit_message_text('Ошибка: нет данных пользователя.')
        return

    current_question = context.user_data.get('current_question')
    if not current_question:
        await query.edit_message_text('Вопрос не найден.')
        return

    user_answer = query.data  # Ответ пользователя из callback_data

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

    await query.edit_message_text(text)
    await handle_next_step(update, context)


async def handle_next_step(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Определяет: задать новый вопрос или завершить викторину."""

    if context.user_data is None:
        return None

    if context.user_data and 'quiz_questions' in context.user_data:
        next_question = context.user_data['quiz_questions'].pop(
            0) if context.user_data['quiz_questions'] else None
    else:
        next_question = None

    if next_question:
        context.user_data['current_question'] = next_question
        await quiz_helpers.ask_next_question(update, context)
    else:
        await quiz_helpers.finish_quiz(update, context)


async def handle_end(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработка кнопки 'Завершить викторину'."""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()

    if context.user_data:
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

    if update.effective_user is None:
        logger.warning('effective_user отсутствует в update.')
        return

    telegram_id = update.effective_user.id
    username = update.effective_user.username

    user, created = await sync_to_async(
        CustomUser.objects.get_or_create)(user_id=telegram_id)

    if not isinstance(update.callback_query.message, Message):
        logger.warning('callback_query.message не является объектом Message.')
        return

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

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()
    await query.edit_message_text(
        text='Эта функция в данный момент не реализована.',
        reply_markup=config_keyboard
    )
