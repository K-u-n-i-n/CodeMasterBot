"""
Запуск бота и добавление обработчиков и задач.
"""

import asyncio
import logging
import os

from django.core.management.base import BaseCommand
from dotenv import load_dotenv
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    commands,
    handlers,
    notifications,
    quiz_mode_handlers,
    utils,
)
from bot.init import get_bot_application

load_dotenv()

WEBHOOK_URL = os.getenv('WEBHOOK_URL')

logging.basicConfig(
    # level=logging.INFO,
    level=logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('app.log'),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запуск бота.'

    def handle(self, *args, **kwargs):
        application = get_bot_application()

        # Обработчики команд
        application.add_handler(CommandHandler('start', commands.start))

        # Обработчики Reply кнопок
        application.add_handler(
            MessageHandler(
                filters.TEXT & filters.Regex('^Меню$'), commands.menu_command
            )
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & filters.Regex('^Викторина$'),
                commands.quiz_command,
            )
        )
        application.add_handler(
            MessageHandler(
                filters.TEXT & filters.Regex('^Бросить кубик$'),
                commands.roll_dice_command,
            )
        )

        # Обработчики текстовых сообщений
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handlers.handle_user_input
            )
        )

        # Обработчики callback запросов
        application.add_handler(
            CallbackQueryHandler(handlers.handle_config, pattern='^conf$')
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_complexity, pattern='^complexity$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_topic_selection, pattern='^topic$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_notifications_settings, pattern='^notify$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_quiz_start, pattern='^question$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_registration, pattern='^registration$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(handlers.handle_end, pattern='^end$')
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_topic_choice, pattern='^(func|expressions)$'
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                notifications.handle_notification_toggle,
                pattern='^(notifications_on|notifications_off)$',
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                notifications.handle_set_notification_time,
                pattern='^set_notification_time$',
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                quiz_mode_handlers.handle_quiz_mode_selection,
                pattern='^quiz_mode_',
            )
        )
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_question_answer,
                pattern='^(?!not_implemented).*',
            )
        )

        # Обработчик для заглушки (функции, которые еще не реализованы)
        application.add_handler(
            CallbackQueryHandler(
                handlers.handle_generic_callback, pattern='not_implemented'
            )
        )

        # Настройка очереди заданий
        job_queue = application.job_queue

        # Планирование ежедневной задачи
        job_queue.run_repeating(
            utils.daily_task, interval=60, first=0, name='daily_task'
        )

        # # Запуск Polling, если не используется Webhook
        # async def delete_webhook():  # Функция для удаления Webhook
        #     await application.bot.delete_webhook()
        #     logger.info('Webhook удален!')
        # application.run_polling()

        # Код для запуска бота в режиме Webhook
        async def set_webhook():
            if not WEBHOOK_URL:
                logger.error('Ошибка: WEBHOOK_URL не установлен!')
                return

            try:
                success = await application.bot.set_webhook(WEBHOOK_URL)
                if success:
                    logger.info(f'Webhook успешно установлен: {WEBHOOK_URL}')
                else:
                    logger.error('Ошибка при установке Webhook!')
            except Exception as e:
                logger.error(f'Ошибка Webhook: {e}')

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        # Устанавливаем Webhook перед запуском
        loop.run_until_complete(set_webhook())

        application.run_webhook(
            listen='0.0.0.0', port=8443, webhook_url=WEBHOOK_URL
        )
