import asyncio
import os
from unittest.mock import AsyncMock, MagicMock

import django
import pytest
from telegram import Bot, Chat, Message, Update, User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()


@pytest.fixture(scope='session')
def event_loop():
    """Создает event loop для async тестов."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_bot():
    """Мок Telegram бота."""
    bot = MagicMock(spec=Bot)
    bot.send_message = AsyncMock()
    bot.edit_message_text = AsyncMock()
    bot.answer_callback_query = AsyncMock()
    return bot


@pytest.fixture
def mock_telegram_update():
    """Мок Telegram Update объекта."""
    # Создаем mock объекты для пользователя
    mock_user = MagicMock(spec=User)
    mock_user.id = 123
    mock_user.first_name = 'Test'
    mock_user.username = 'test_user'
    mock_user.is_bot = False

    # Создаем mock объект для чата
    mock_chat = MagicMock(spec=Chat)
    mock_chat.id = 123
    mock_chat.type = 'private'

    # Создаем mock объект для сообщения
    mock_message = MagicMock(spec=Message)
    mock_message.text = 'Test message'
    mock_message.reply_text = AsyncMock()
    mock_message.chat = mock_chat
    mock_message.from_user = mock_user
    mock_message.message_id = 1

    # Создаем mock объект для Update
    update = MagicMock(spec=Update)
    update.effective_user = mock_user
    update.effective_chat = mock_chat
    update.message = mock_message
    update.callback_query = None
    update.update_id = 1

    return update


@pytest.fixture
def mock_telegram_context(mock_bot):
    """Мок Telegram Context объекта."""
    from telegram.ext import CallbackContext

    mock_context = MagicMock(spec=CallbackContext)
    mock_context.user_data = {}
    mock_context.chat_data = {}
    mock_context.bot_data = {}
    mock_context.bot = mock_bot
    mock_context.args = []

    return mock_context


@pytest.fixture
def sample_user_data():
    """Возвращает тестовые данные пользователя."""
    return {
        'user_id': 12345,
        'username': 'test_user',
        'difficulty': 'easy',
        'tag': 'func',
    }


@pytest.fixture
def sample_code_request():
    """Пример запроса на генерацию кода."""
    return {
        'language': 'python',
        'description': 'Создай функцию для сортировки списка',
        'requirements': [
            'Использовать встроенные функции',
            'Добавить docstring',
        ],
    }
