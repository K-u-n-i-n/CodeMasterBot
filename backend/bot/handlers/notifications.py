import logging
from datetime import datetime
from typing import Optional

from asgiref.sync import sync_to_async
from telegram import Message, Update
from telegram.ext import ContextTypes

from bot.handlers import context_helpers, db_helpers, keyboards, utils

logger = logging.getLogger(__name__)


async def handle_notification_toggle(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает включение и выключение уведомлений."""

    logger.info('Начало обработки запроса вкл/выкл уведомлений.')

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()

    user_id = query.from_user.id
    user = await db_helpers.get_user_from_db(user_id)

    if not user:
        await utils.send_response_message(
            query, 'Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию.'
        )
        return

    settings = await db_helpers.get_or_create_user_settings(user)

    if query.data == 'notifications_on':
        settings.notification = True
        await query.edit_message_text(
            text='🔔 Уведомления включены!',
            reply_markup=keyboards.notification_time_keyboard
        )

    elif query.data == 'notifications_off':
        settings.notification = False
        await query.edit_message_text(
            text='🔕 Уведомления отключены.',
            reply_markup=keyboards.config_keyboard
        )

    await sync_to_async(settings.save)()
    await query.answer()


async def handle_set_notification_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает нажатие кнопки 'Настроить время'."""

    logger.info('Начало обработки запроса на настройку времени уведомлений.')

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.edit_message_text(
        text=(
            'Введите время для уведомлений в формате '
            'ЧЧ:ММ (например, 07:00):'
        )
    )

    if context.user_data is None:
        return None

    context.user_data['awaiting_notification_time'] = True
    await query.answer()


async def handle_notification_time_input(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод времени для уведомлений."""

    logger.info('Начало обработки ввода времени уведомлений.')

    if context.user_data is None or not context.user_data.get(
        'awaiting_notification_time'
    ):
        return

    message: Optional[Message] = update.message
    if message is None or message.text is None or message.from_user is None:
        return

    user_id: int = message.from_user.id
    user = await db_helpers.get_user_from_db(user_id)
    if not user:
        await message.reply_text(
            'Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию.'
        )
        return

    settings = await db_helpers.get_or_create_user_settings(user)

    try:
        notification_time = datetime.strptime(message.text, '%H:%M').time()
        settings.notification_time = notification_time
        await sync_to_async(settings.save)()

        await message.reply_text(
            'Время уведомлений установлено на '
            f'{notification_time.strftime("%H:%M")} (UTC).',
            reply_markup=keyboards.notification_time_keyboard
        )

    except ValueError:
        await message.reply_text(
            '❌ Некорректный формат времени.\n'
            'Введите время в формате ЧЧ:ММ (например, 07:00).',
            reply_markup=keyboards.notification_time_keyboard
        )

    context.user_data['awaiting_notification_time'] = False
