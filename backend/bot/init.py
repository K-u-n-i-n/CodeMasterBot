from django.conf import settings
from telegram.ext import ApplicationBuilder


def get_bot_application():
    """Создает и возвращает экземпляр Telegram Bot Application."""

    return ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
