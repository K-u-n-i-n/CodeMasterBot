"""
Модуль-обработчик для команд бота.
"""

import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, CallbackContext

from .handlers import handle_quiz_start
from .keyboards import menu_keyboard


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""

    if update.message is None:
        return

    reply_keyboard = [
        [KeyboardButton('Меню'), KeyboardButton('Викторина')],
        [KeyboardButton('Бросить кубик')],
    ]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await update.message.reply_text(
        'Тут будет информация о тестах.\n\nВыберите одну из опций ниже.',
        reply_markup=reply_markup,
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для кнопки Меню"""

    if update.message is None:
        return

    await update.message.reply_text(
        'Выберите, пожалуйста:', reply_markup=menu_keyboard
    )


async def roll_dice_command(update: Update, context: CallbackContext):
    """Обработчик для Reply-кнопки (Бросить кубик)"""

    if update.message is None:
        return

    logging.info('Запуск roll_dice_command')
    await update.message.reply_dice()


async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик для Reply-кнопки (Викторина)"""

    await handle_quiz_start(update, context)
