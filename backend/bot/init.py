import logging

from django.conf import settings
from telegram.ext import ApplicationBuilder

logger = logging.getLogger(__name__)


def get_bot_application():
    """Создает и возвращает экземпляр Telegram Bot Application."""

    logger.info('Создание экземпляра Telegram Bot Application')

    return ApplicationBuilder().token(settings.TELEGRAM_TOKEN).build()
