from datetime import datetime

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import db_helpers, context_helpers, keyboards


async def handle_notification_toggle(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает включение и выключение уведомлений."""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.answer()

    user_id = query.from_user.id
    user = await db_helpers.get_user_from_db(user_id)
    if not user:
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
            text='🔕 Уведомления отключены.'
        )
        # # Возвращаемся в главное меню настроек
        # await handlers.handle_my_settings(update, context)

    await sync_to_async(settings.save)()
    await query.answer()


async def handle_set_notification_time(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Обрабатывает нажатие кнопки 'Настроить время'."""

    query = context_helpers.get_callback_query(update)
    if not query:
        return

    await query.edit_message_text(
        text=(
            'Введите время для уведомлений в формате '
            'ЧЧ:ММ (например, 07:00):'
        )
    )
    context.user_data['awaiting_notification_time'] = True
    await query.answer()


async def handle_notification_time_input(
        update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обрабатывает ввод времени для уведомлений."""

    if not context.user_data.get('awaiting_notification_time'):
        return

    user_id = update.message.from_user.id
    user = await db_helpers.get_user_from_db(user_id)
    if not user:
        return

    settings = await db_helpers.get_or_create_user_settings(user)

    try:
        notification_time = datetime.strptime(
            update.message.text, '%H:%M').time()
        settings.notification_time = notification_time
        await sync_to_async(settings.save)()
        await update.message.reply_text(
            f'Время уведомлений установлено на {
                notification_time.strftime("%H:%M")}.'
        )
    except ValueError:
        await update.message.reply_text(
            'Некорректный формат времени.'
            'Введите время в формате ЧЧ:ММ (например, 07:00).'
        )

    context.user_data['awaiting_notification_time'] = False
