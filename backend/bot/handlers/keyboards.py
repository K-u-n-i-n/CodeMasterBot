"""
Модуль содержит функции генерации клавиатур.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Клавиатура для Меню
menu_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Настроить бота', callback_data='conf'),
        InlineKeyboardButton('Информация о боте', callback_data='info'),
    ],
    [InlineKeyboardButton('Регистрация', callback_data='registration')],
])


# Клавиатура для настройки бота
config_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Сложность', callback_data='complexity'),
        InlineKeyboardButton('Тема', callback_data='topic'),
    ], [InlineKeyboardButton('Настроить оповещение', callback_data='notify'),]
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
            'Функции/Методы', callback_data='not_implemented'),
        InlineKeyboardButton('Выражения', callback_data='not_implemented'),
    ],
])

# Клавиатура для продолжения или завершения викторины
next_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('Далее', callback_data='next'),
        InlineKeyboardButton('Завершить викторину', callback_data='end'),
    ]
])

# Клавиатура для выбора настроек оповещения
notification_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton('ВКЛ', callback_data='not_implemented'),
        InlineKeyboardButton('ВЫКЛ', callback_data='not_implemented'),
    ],
    [InlineKeyboardButton('Настроить время', callback_data='not_implemented'),]
])
