"""
Enterprise Configuration Validation Schemas
Централизованные Pydantic схемы для валидации конфигурации Dynaconf
"""

from .database import DatabaseConfig
from .security import SecurityConfig
from .telegram import TelegramConfig

__all__ = [
    'DatabaseConfig',
    'TelegramConfig',
    'SecurityConfig',
]


def validate_all_configs(**config_data):
    """
    Валидация всех конфигураций одновременно
    Используется при инициализации приложения
    """
    errors = []

    try:
        DatabaseConfig(**config_data.get('database', {}))
    except Exception as e:
        errors.append(f'Database config error: {e}')

    try:
        TelegramConfig(**config_data.get('telegram', {}))
    except Exception as e:
        errors.append(f'Telegram config error: {e}')

    try:
        SecurityConfig(**config_data.get('security', {}))
    except Exception as e:
        errors.append(f'Security config error: {e}')

    if errors:
        raise ValueError(
            f'Configuration validation failed: {"; ".join(errors)}'
        )

    return True
