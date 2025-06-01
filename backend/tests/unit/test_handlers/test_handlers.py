from unittest.mock import AsyncMock, MagicMock

import pytest
from bot.handlers import commands, handlers
from bot.models import CustomUser, Tag


@pytest.mark.integration
class TestCriticalHandlers:
    """Критические smoke-тесты для обработчиков бота"""

    @pytest.mark.asyncio
    async def test_start_command_not_crashes(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Smoke-тест: команда /start не падает"""
        try:
            await commands.start(mock_telegram_update, mock_telegram_context)
            # Если дошли сюда - обработчик не упал
            assert True
        except Exception as e:
            pytest.fail(f'Команда /start упала с ошибкой: {e}')

    @pytest.mark.asyncio
    async def test_menu_command_not_crashes(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Smoke-тест: команда меню не падает"""
        try:
            await commands.menu_command(
                mock_telegram_update, mock_telegram_context
            )
            assert True
        except Exception as e:
            pytest.fail(f'Команда меню упала с ошибкой: {e}')

    @pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
    @pytest.mark.asyncio
    async def test_quiz_command_not_crashes(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Smoke-тест: команда викторины не падает"""
        try:
            await commands.quiz_command(
                mock_telegram_update, mock_telegram_context
            )
            assert True
        except Exception as e:
            pytest.fail(f'Команда викторины упала с ошибкой: {e}')

    @pytest.mark.asyncio
    async def test_roll_dice_command_not_crashes(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Smoke-тест: команда кубика не падает"""
        try:
            await commands.roll_dice_command(
                mock_telegram_update, mock_telegram_context
            )
            assert True
        except Exception as e:
            pytest.fail(f'Команда кубика упала с ошибкой: {e}')


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
class TestCriticalHandlersWithMocks:
    """Критические тесты с моками для проверки логики"""

    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_handle_config_with_no_settings(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Тест настроек когда у пользователя нет сохраненных настроек"""
        # Мокаем callback_query
        mock_telegram_update.callback_query = MagicMock()
        mock_telegram_update.callback_query.from_user.id = 12345
        mock_telegram_update.callback_query.answer = AsyncMock()
        mock_telegram_update.callback_query.edit_message_text = AsyncMock()

        try:
            await handlers.handle_config(
                mock_telegram_update, mock_telegram_context
            )
            # Проверяем что edit_message_text был вызван
            edit_call = mock_telegram_update.callback_query.edit_message_text
            edit_call.assert_called_once()
            assert True
        except Exception as e:
            pytest.fail(f'handle_config упал с ошибкой: {e}')

    @pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
    @pytest.mark.asyncio
    @pytest.mark.django_db
    async def test_handle_registration_new_user(
        self, mock_telegram_update, mock_telegram_context
    ):
        """Тест регистрации нового пользователя"""
        # Настраиваем мок для регистрации
        mock_telegram_update.callback_query = MagicMock()
        mock_telegram_update.callback_query.data = 'registration'
        mock_telegram_update.callback_query.answer = AsyncMock()
        mock_telegram_update.callback_query.message = MagicMock()
        mock_telegram_update.callback_query.message.reply_text = AsyncMock()
        mock_telegram_update.effective_user = MagicMock()
        mock_telegram_update.effective_user.id = 99999  # Новый ID
        mock_telegram_update.effective_user.username = 'new_test_user'

        try:
            await handlers.handle_registration(
                mock_telegram_update, mock_telegram_context
            )
            # Проверяем что ответ был отправлен
            reply_call = mock_telegram_update.callback_query.message.reply_text
            reply_call.assert_called_once()
            assert True
        except Exception as e:
            pytest.fail(f'handle_registration упал с ошибкой: {e}')


class TestCriticalImportsAndConnections:
    """Критические тесты импортов и подключений"""

    def test_handlers_module_imports(self):
        """Тест что модуль handlers импортируется без ошибок"""
        try:
            from bot.handlers import commands, handlers, keyboards

            assert handlers is not None
            assert commands is not None
            assert keyboards is not None
        except ImportError as e:
            pytest.fail(f'Ошибка импорта модулей handlers: {e}')

    def test_models_import(self):
        """Тест что модели импортируются без ошибок"""
        try:
            from bot.models import CustomUser, Question, Tag, UserSettings

            assert CustomUser is not None
            assert Tag is not None
            assert Question is not None
            assert UserSettings is not None
        except ImportError as e:
            pytest.fail(f'Ошибка импорта моделей: {e}')

    def test_telegram_imports(self):
        """Тест что Telegram библиотеки доступны"""
        try:
            from telegram import Update
            from telegram.ext import ContextTypes

            assert Update is not None
            assert ContextTypes is not None
        except ImportError as e:
            pytest.fail(f'Ошибка импорта Telegram библиотек: {e}')


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
class TestCriticalDatabaseQueries:
    """Критические тесты базовых запросов к БД"""

    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_user_creation_in_handlers(self):
        """Тест создания пользователя через handlers"""
        from asgiref.sync import sync_to_async

        try:
            # Имитируем создание пользователя как в реальном коде
            user, created = await sync_to_async(
                CustomUser.objects.get_or_create
            )(user_id=88888)
            assert user is not None
            assert created is True
        except Exception as e:
            pytest.fail(f'Ошибка создания пользователя: {e}')

    @pytest.mark.django_db
    def test_tag_exists_for_quiz(self):
        """Тест что базовые теги существуют для викторины"""
        try:
            # Создаем базовый тег если его нет
            tag, created = Tag.objects.get_or_create(
                slug='func', defaults={'name': 'Функции'}
            )
            assert tag is not None
            assert tag.slug == 'func'
        except Exception as e:
            pytest.fail(f'Ошибка работы с тегами: {e}')
