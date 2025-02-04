"""
Модуль содержит функции генерации клавиатур.
"""
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

HELP_URL = os.getenv('HELP_URL')


# Клавиатура для Меню
menu_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Настроить бота', callback_data='conf'),
        InlineKeyboardButton('Информация о боте', url=HELP_URL),
    ],
    [InlineKeyboardButton('Мои настройки', callback_data='my_settings')],
    [InlineKeyboardButton('Зарегистрироваться', callback_data='registration')],
])


# Клавиатура для настройки бота
config_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Сложность', callback_data='complexity'),
        InlineKeyboardButton('Тема', callback_data='topic'),
    ], [InlineKeyboardButton('Настроить оповещение', callback_data='notify'),],
    [InlineKeyboardButton('Мои настройки', callback_data='my_settings')],
])

# Клавиатура для выбора сложности викторины
complexity_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Easy', callback_data='not_implemented'),
        InlineKeyboardButton('Hard', callback_data='not_implemented'),
    ],
])

# Клавиатура для выбора темы викторины
topic_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            'Функции', callback_data='func'),
        InlineKeyboardButton(
            'Выражения', callback_data='expressions'),
    ],
])

# Клавиатура для вкл/откл оповещения
notification_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('ВКЛ', callback_data='notifications_on'),
        InlineKeyboardButton('ВЫКЛ', callback_data='notifications_off'),
    ],
])

# Клавиатура для настройки времени оповещения
notification_time_keyboard = InlineKeyboardMarkup([
    [InlineKeyboardButton(
        'Настроить время', callback_data='set_notification_time')]
])
