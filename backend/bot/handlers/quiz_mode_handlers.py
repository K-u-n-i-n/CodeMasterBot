import logging

from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers import db_helpers, keyboards

logger = logging.getLogger(__name__)


async def handle_quiz_mode_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Обработка нажатия кнопки выбора режима викторины.
    callback_data: 'quiz_mode_easy' или 'quiz_mode_hard'
    """

    logger.info('Обработка нажатия кнопки выбора режима викторины.')

    query = update.callback_query
    if query is None:
        logger.warning('query отсутствует.')
        return

    await query.answer()

    mode = query.data  # Получаем выбранный режим
    if mode == 'quiz_mode_easy':
        new_mode = 'easy'
    elif mode == 'quiz_mode_hard':
        new_mode = 'hard'
    else:
        await query.edit_message_text('Неизвестный режим.')
        return

    user_id = query.from_user.id
    user_settings, has_settings = await db_helpers.get_user_settings(user_id)

    # if not has_settings:
    #     await query.edit_message_text(
    #         'Ошибка: настройки пользователя не найдены.'
    #     )
    #     return

    if isinstance(user_settings, dict):
        user_settings['difficulty'] = new_mode
    else:
        user_settings.difficulty = new_mode
        await sync_to_async(user_settings.save)()

    if context.user_data is not None:
        context.user_data['difficulty'] = new_mode

    logger.info(f'Установлен режим: {new_mode}')
    await query.edit_message_text(
        f'Режим викторины установлен на {new_mode}.',
        reply_markup=keyboards.complexity_keyboard,
    )
