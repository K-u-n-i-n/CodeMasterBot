"""
Модуль-обработчик для команд бота.
"""

import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext

from .handlers import handle_quiz_start
from .keyboards import menu_keyboard

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""

    logger.info('Запуск start')

    if update.message is None:
        return

    reply_keyboard = [
        [KeyboardButton('Меню'), KeyboardButton('Викторина')],
        [KeyboardButton('Бросить кубик')],
    ]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Привет! 👋 Я CodeMasterBot.\n\n'
        'Готов проверить свои знания?\n'
        'Нажимай кнопку "Викторина"\nи погнали! 🎉\n\n'
        'Если хочешь узнать о боте или настроить его под себя, жми "Меню".',
        reply_markup=reply_markup,
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для кнопки Меню"""

    logger.info('Запуск menu_command')

    if update.message is None:
        return

    await update.message.reply_text(
        'Выберите, пожалуйста:', reply_markup=menu_keyboard
    )


async def roll_dice_command(update: Update, context: CallbackContext):
    """Обработчик для Reply-кнопки (Бросить кубик)"""

    logger.info('Запуск roll_dice_command')

    if update.message is None:
        return

    await update.message.reply_dice()


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для Reply-кнопки (Викторина)"""

    logger.info('Запуск quiz_command')

    await handle_quiz_start(update, context)
