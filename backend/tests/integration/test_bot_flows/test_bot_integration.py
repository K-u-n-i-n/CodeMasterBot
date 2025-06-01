from unittest.mock import AsyncMock, MagicMock

import pytest
from bot.handlers import commands, handlers
from bot.models import CustomUser, Question, Tag


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.integration
@pytest.mark.django_db
class TestBotIntegrationFlow:
    """Интеграционные тесты полного потока работы бота"""

    @pytest.mark.asyncio
    async def test_user_registration_flow(
        self, mock_telegram_update, mock_telegram_context
    ):
        """
        Тест полного flow регистрации пользователя.

        Memory note: Полный flow от команды start до создания пользователя в БД
        """
        # Arrange
        user_id = 99999
        username = 'integration_test_user'

        mock_telegram_update.effective_user.id = user_id
        mock_telegram_update.effective_user.username = username

        # Убеждаемся что пользователя нет в БД
        assert not CustomUser.objects.filter(user_id=user_id).exists()

        # Act - выполняем команду start
        await commands.start(mock_telegram_update, mock_telegram_context)

        # Assert - проверяем что пользователь создан
        user = CustomUser.objects.get(user_id=user_id)
        assert user.username == username
        assert user.user_id == user_id

    @pytest.mark.asyncio
    async def test_quiz_flow_with_tags(
        self, mock_telegram_update, mock_telegram_context
    ):
        """
        Тест flow викторины с существующими тегами.

        Memory note: Интеграция викторины с реальными данными БД
        """
        # Arrange - создаем тестовые данные
        tag = Tag.objects.create(name='Тестовые функции', slug='test_func')
        user = CustomUser.objects.create(user_id=88888, username='quiz_user')

        question = Question.objects.create(
            text='Что делает функция len()?',
            correct_answer='Возвращает длину объекта',
            difficulty='easy',
        )
        question.tags.add(tag)

        mock_telegram_update.effective_user.id = user.user_id

        # Act - запускаем викторину
        try:
            await commands.quiz_command(
                mock_telegram_update, mock_telegram_context
            )
            assert True  # Команда не упала
        except Exception as e:
            pytest.fail(f'Интеграционный тест викторины упал: {e}')

    @pytest.mark.asyncio
    async def test_settings_flow_integration(
        self, mock_telegram_update, mock_telegram_context
    ):
        """
        Тест flow настроек пользователя с БД.

        Memory note: Интеграция настроек пользователя с callback_query
        """
        # Arrange
        user = CustomUser.objects.create(
            user_id=77777, username='settings_user'
        )

        # Мокаем callback_query для настроек
        mock_telegram_update.callback_query = MagicMock()
        mock_telegram_update.callback_query.from_user.id = user.user_id
        mock_telegram_update.callback_query.answer = AsyncMock()
        mock_telegram_update.callback_query.edit_message_text = AsyncMock()

        # Act
        try:
            await handlers.handle_config(
                mock_telegram_update, mock_telegram_context
            )

            # Assert - проверяем что ответ был отправлен
            mock_telegram_update.callback_query.edit_message_text.assert_called_once()
            assert True
        except Exception as e:
            pytest.fail(f'Интеграционный тест настроек упал: {e}')


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.integration
@pytest.mark.django_db
class TestDatabaseIntegration:
    """Интеграционные тесты взаимодействия с базой данных"""

    def test_user_creation_with_tags_and_questions(self):
        """
        Тест создания связанных объектов в БД.

        Memory note: Паттерн для тестирования связей между моделями
        """
        # Arrange & Act
        user = CustomUser.objects.create(
            user_id=66666, username='db_test_user'
        )
        tag1 = Tag.objects.create(name='Циклы', slug='loops')
        tag2 = Tag.objects.create(name='Условия', slug='conditions')

        question = Question.objects.create(
            text='Какой цикл использовать для итерации?',
            correct_answer='for',
            difficulty='medium',
        )
        question.tags.add(tag1, tag2)

        # Assert
        assert user.user_id == 66666
        assert tag1.questions.count() == 1
        assert tag2.questions.count() == 1
        assert question.tags.count() == 2
        assert question in tag1.questions.all()
        assert question in tag2.questions.all()

    def test_user_settings_creation_and_update(self):
        """
        Тест создания и обновления настроек пользователя.

        Memory note: Паттерн для тестирования UserSettings с foreign key
        """
        # Arrange
        user = CustomUser.objects.create(
            user_id=55555, username='settings_test'
        )
        tag = Tag.objects.create(name='Настройки', slug='settings')

        # Act - создаем настройки
        from bot.models import UserSettings

        settings = UserSettings.objects.create(
            user=user, difficulty='hard', tag=tag, notification_time='09:00'
        )

        # Assert
        assert settings.user == user
        assert settings.difficulty == 'hard'
        assert settings.tag == tag
        assert settings.notification_time.strftime('%H:%M') == '09:00'

        # Act - обновляем настройки
        settings.difficulty = 'easy'
        settings.save()

        # Assert - проверяем обновление
        updated_settings = UserSettings.objects.get(user=user)
        assert updated_settings.difficulty == 'easy'
