import pytest
from bot.models import CustomUser, Question, Tag, UserSettings
from django.db import IntegrityError


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.unit
@pytest.mark.django_db
class TestCustomUserModel:
    """Критические тесты модели CustomUser"""

    def test_create_user(self):
        """Тест создания пользователя"""
        user = CustomUser.objects.create(user_id=12345, username='test_user')
        assert user.user_id == 12345
        assert user.username == 'test_user'
        assert str(user) == 'test_user'

    def test_user_id_unique_constraint(self):
        """Тест уникальности user_id"""
        CustomUser.objects.create(user_id=12345, username='user1')

        with pytest.raises(IntegrityError):
            CustomUser.objects.create(user_id=12345, username='user2')

    def test_user_str_method_with_no_username(self):
        """Тест строкового представления без username"""
        user = CustomUser.objects.create(user_id=54321)
        assert str(user) == 'Пользователь 54321'


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.unit
@pytest.mark.django_db
class TestTagModel:
    """Критические тесты модели Tag"""

    def test_create_tag(self):
        """Тест создания тега"""
        tag = Tag.objects.create(name='Функции', slug='func')
        assert tag.name == 'Функции'
        assert tag.slug == 'func'
        assert str(tag) == 'Функции'

    def test_tag_name_unique_constraint(self):
        """Тест уникальности имени тега"""
        Tag.objects.create(name='Функции', slug='func')

        with pytest.raises(IntegrityError):
            Tag.objects.create(name='Функции', slug='func2')


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.unit
@pytest.mark.django_db
class TestQuestionModel:
    """Критические тесты модели Question"""

    def test_create_question(self):
        """Тест создания вопроса"""
        question = Question.objects.create(
            name='len',
            description='Возвращает длину объекта',
            syntax='len(obj)',
        )
        assert question.name == 'len'
        assert question.description == 'Возвращает длину объекта'
        assert str(question) == 'len'

    def test_question_name_unique_constraint(self):
        """Тест уникальности имени вопроса"""
        Question.objects.create(name='len', description='Первое описание')

        with pytest.raises(IntegrityError):
            Question.objects.create(name='len', description='Второе описание')


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.unit
@pytest.mark.django_db
class TestUserSettingsModel:
    """Критические тесты модели UserSettings"""

    def test_create_user_settings(self):
        """Тест создания настроек пользователя"""
        user = CustomUser.objects.create(user_id=12345)
        tag = Tag.objects.create(name='Функции', slug='func')

        settings = UserSettings.objects.create(
            user=user, tag=tag, difficulty='easy', notification=True
        )

        assert settings.user == user
        assert settings.tag == tag
        assert settings.difficulty == 'easy'
        assert settings.notification is True


@pytest.mark.skip(reason='Временно отключено до внедрения Динакорф')
@pytest.mark.unit
@pytest.mark.django_db
class TestDatabaseBasicOperations:
    """Критические тесты базовых операций с БД"""

    def test_database_connection(self):
        """Тест подключения к БД"""
        # Простой тест - создание объекта должно пройти без ошибок
        user_count_before = CustomUser.objects.count()
        CustomUser.objects.create(user_id=99999)
        user_count_after = CustomUser.objects.count()

        assert user_count_after == user_count_before + 1

    def test_foreign_key_relationship(self):
        """Тест связей между моделями"""
        user = CustomUser.objects.create(user_id=12345)
        tag = Tag.objects.create(name='Тест', slug='test')

        # Создаем настройки с связью
        settings = UserSettings.objects.create(
            user=user, tag=tag, difficulty='hard'
        )

        # Проверяем обратные связи
        assert settings in user.settings.all()
        assert tag == settings.tag
