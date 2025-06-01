"""
Тесты запуска и конфигурации Django сервера.

Эти тесты проверяют что Django приложение может корректно запуститься
и что все настройки сконфигурированы правильно.
Эквивалент команды: python manage.py runserver
"""

import sys
from io import StringIO

import pytest
from django.conf import settings
from django.core.management.commands.check import Command
from django.test import Client
from django.urls import NoReverseMatch, get_resolver, reverse


class TestDjangoServerStartup:
    """Критические тесты запуска Django сервера"""

    def test_django_server_can_start(self):
        """
        Критический тест: Django приложение может запуститься без ошибок.

        Эквивалент команды: python manage.py runserver
        Проверяет:
        - Корректность настроек Django
        - Валидность URL patterns
        - Django system check
        """
        # Проверяем что настройки загружаются корректно
        assert settings.SECRET_KEY is not None, (
            'SECRET_KEY должен быть настроен'
        )
        assert settings.DATABASES is not None, (
            'DATABASES должны быть настроены'
        )

        # Проверяем что URL patterns загружаются без ошибок
        resolver = get_resolver()
        assert resolver is not None, 'URL resolver должен быть доступен'

        # Проверяем что можем получить список URL patterns
        url_patterns = resolver.url_patterns
        assert url_patterns is not None, 'URL patterns должны загружаться'

        # Проверяем что Django может выполнить system check
        # Аналог: python manage.py check
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            check_command = Command()
            check_command.check(
                app_configs=None,
                tags=None,
                display_num_errors=False,
                include_deployment_checks=False,
                fail_level='ERROR',
            )
            # Если дошли сюда без исключений - проверки прошли успешно
        except Exception as e:
            pytest.fail(f'Django system check упал с ошибкой: {e}')
        finally:
            sys.stdout = old_stdout

    def test_django_urls_configuration(self):
        """
        Тест корректности URL конфигурации.

        Проверяет что URL routing работает и тестовый клиент может создаться.
        """
        # Проверяем что можем создать Django Test Client
        client = Client()
        assert client is not None, 'Django Test Client должен создаваться'

        # Проверяем админку (если настроена)
        try:
            admin_url = reverse('admin:index')
            assert admin_url == '/admin/', 'Админ URL должен быть /admin/'
        except NoReverseMatch:
            # Админка может быть не настроена - это не критично для основного функционала
            pass

    def test_django_settings_validation(self):
        """
        Дополнительная валидация критических настроек Django.
        """
        # Проверяем базовые настройки безопасности
        assert hasattr(settings, 'SECRET_KEY'), (
            'SECRET_KEY должен быть определен'
        )
        assert len(settings.SECRET_KEY) > 10, (
            'SECRET_KEY должен быть достаточно длинным'
        )

        # Проверяем настройки БД
        assert 'default' in settings.DATABASES, (
            "База данных 'default' должна быть настроена"
        )
        default_db = settings.DATABASES['default']
        assert 'ENGINE' in default_db, 'DATABASE ENGINE должен быть указан'
        # Проверяем что приложения настроены
        bot_app_configured = any(
            'bot' in app for app in settings.INSTALLED_APPS
        )
        assert bot_app_configured, (
            "Приложение 'bot' должно быть в INSTALLED_APPS"
        )
        assert 'django.contrib.admin' in settings.INSTALLED_APPS, (
            'Admin должен быть в INSTALLED_APPS'
        )
