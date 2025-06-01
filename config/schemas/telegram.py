"""
Pydantic схемы для валидации настроек Telegram Bot
Enterprise подход к управлению настроек бота
"""

from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class TelegramConfig(BaseModel):
    """Конфигурация Telegram Bot"""

    token: str = Field(description='Telegram Bot Token (from env variable)')
    webhook_enabled: bool = Field(
        default=False, description='Enable webhook mode'
    )
    polling_enabled: bool = Field(
        default=True, description='Enable polling mode'
    )
    webhook_url: Optional[HttpUrl] = Field(
        default=None, description='Webhook URL'
    )

    @validator('token')
    def validate_token(cls, v):
        if not v:
            raise ValueError('Telegram token cannot be empty')
        # Базовая проверка формата Telegram токена (bot123456:ABC-DEF...)
        if ':' not in v or len(v) < 20:
            raise ValueError('Invalid Telegram token format')
        return v

    @validator('webhook_url')
    def validate_webhook_url(cls, v, values):
        webhook_enabled = values.get('webhook_enabled', False)
        if webhook_enabled and not v:
            raise ValueError('Webhook URL required when webhook is enabled')
        if not webhook_enabled and v:
            raise ValueError('Webhook URL provided but webhook is disabled')
        return v

    @validator('polling_enabled')
    def validate_polling_vs_webhook(cls, v, values):
        webhook_enabled = values.get('webhook_enabled', False)
        if v and webhook_enabled:
            raise ValueError(
                'Cannot enable both polling and webhook simultaneously'
            )
        if not v and not webhook_enabled:
            raise ValueError('Either polling or webhook must be enabled')
        return v

    class Config:
        validate_assignment = True
        extra = 'forbid'
