"""
Запуск бота и добавление обработчиков и задач.
"""

import logging
from datetime import time

from django.core.management.base import BaseCommand
from django.conf import settings
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from bot.handlers import handlers, utils, commands


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


class Command(BaseCommand):
    help = 'Запуск бота.'

    def handle(self, *args, **kwargs):
        application = ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()

        # Обработчики команд
        application.add_handler(CommandHandler('start', commands.start))

        # Обработчики Reply кнопок
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex('^Меню$'),
            commands.menu_command))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex('^Викторина$'),
            commands.quiz_command))
        application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex('^Бросить кубик$'),
            commands.roll_dice_command))

        # Обработчики callback запросов
        application.add_handler(CallbackQueryHandler(
            handlers.handle_config, pattern='conf'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_complexity, pattern='complexity'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_topic_selection, pattern='topic'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_notifications_settings, pattern='notify'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_help_info, pattern='info'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_quiz_start, pattern='question'))
        application.add_handler(CallbackQueryHandler(
            handlers.handle_registration, pattern='registration'))
        # Функция - затычка
        application.add_handler(CallbackQueryHandler(
            handlers.handle_generic_callback, pattern='not_implemented'))
        # Функция для ответов на вопросы
        application.add_handler(CallbackQueryHandler(
            handlers.handle_question_answer, pattern='^(?!next|end).*'))
        # Регистрация CallbackQueryHandler для обработки 'Далее' и 'Завершить викторину'
        application.add_handler(CallbackQueryHandler(
            handlers.handle_next_or_end, pattern='^(next|end)$'))

        # Настройка очереди заданий
        job_queue = application.job_queue

        # Планирование ежедневной задачи
        job_queue.run_daily(
            utils.daily_task, time=time(hour=6, minute=0, second=0),
            name='daily_task'
        )

        application.run_polling()
