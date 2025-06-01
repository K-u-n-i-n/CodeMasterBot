"""
Pydantic схемы для валидации настроек безопасности
Enterprise подход к управлению настройками безопасности
"""

from typing import List

from pydantic import BaseModel, Field, validator


class SecurityConfig(BaseModel):
    """Конфигурация безопасности Django"""

    secret_key: str = Field(
        description='Django SECRET_KEY (from env variable)'
    )
    debug: bool = Field(default=False, description='Django DEBUG mode')
    allowed_hosts: List[str] = Field(
        default=[], description='Django ALLOWED_HOSTS'
    )

    # HTTPS настройки
    secure_ssl_redirect: bool = Field(
        default=False, description='Force HTTPS redirect'
    )
    secure_hsts_seconds: int = Field(
        default=0, description='HSTS header seconds'
    )
    secure_hsts_include_subdomains: bool = Field(
        default=False, description='HSTS subdomains'
    )
    secure_hsts_preload: bool = Field(
        default=False, description='HSTS preload'
    )

    # Cookie настройки
    session_cookie_secure: bool = Field(
        default=False, description='Secure session cookies'
    )
    csrf_cookie_secure: bool = Field(
        default=False, description='Secure CSRF cookies'
    )
    session_cookie_httponly: bool = Field(
        default=True, description='HTTPOnly session cookies'
    )
    csrf_cookie_httponly: bool = Field(
        default=True, description='HTTPOnly CSRF cookies'
    )

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if not v:
            raise ValueError('SECRET_KEY cannot be empty')
        if len(v) < 50:
            raise ValueError('SECRET_KEY must be at least 50 characters long')
        if v.startswith('django-insecure-') and len(set(v)) < 10:
            raise ValueError(
                'SECRET_KEY appears to be insecure (too few unique characters)'
            )
        return v

    @validator('allowed_hosts')
    def validate_allowed_hosts(cls, v, values):
        debug = values.get('debug', False)
        if not debug and not v:
            raise ValueError(
                'ALLOWED_HOSTS cannot be empty in production (DEBUG=False)'
            )
        if debug and '*' in v:
            # В debug режиме '*' допустимо, но предупреждаем
            pass
        return v

    @validator('secure_hsts_seconds')
    def validate_hsts_seconds(cls, v, values):
        if v < 0:
            raise ValueError('HSTS seconds cannot be negative')
        if v > 0 and v < 3600:
            raise ValueError(
                'HSTS seconds should be at least 3600 (1 hour) if enabled'
            )
        return v

    @validator('session_cookie_secure')
    def validate_cookie_security(cls, v, values):
        ssl_redirect = values.get('secure_ssl_redirect', False)
        if ssl_redirect and not v:
            raise ValueError(
                'Secure cookies should be enabled when SSL redirect is on'
            )
        return v

    class Config:
        validate_assignment = True
        extra = 'forbid'
