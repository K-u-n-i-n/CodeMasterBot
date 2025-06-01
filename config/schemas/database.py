"""
Pydantic схемы для валидации конфигурации базы данных
Enterprise подход к управлению настройками БД
"""

from typing import Literal

from pydantic import BaseModel, Field, validator


class DatabaseConfig(BaseModel):
    """Конфигурация базы данных"""

    engine: Literal[
        'django.db.backends.sqlite3', 'django.db.backends.postgresql'
    ] = Field(description='Django database backend')

    name: str = Field(description='Database name or path')
    host: str = Field(default='localhost', description='Database host')
    port: str = Field(default='5432', description='Database port')
    user: str = Field(default='', description='Database user (from env)')
    password: str = Field(
        default='', description='Database password (from env)'
    )

    @validator('name')
    def validate_name(cls, v, values):
        engine = values.get('engine', '')
        if engine == 'django.db.backends.sqlite3':
            # SQLite может быть :memory: или файл
            return v
        elif engine == 'django.db.backends.postgresql':
            if not v or len(v) < 3:
                raise ValueError(
                    'PostgreSQL database name must be at least 3 characters'
                )
        return v

    @validator('port')
    def validate_port(cls, v):
        try:
            port_int = int(v)
            if not (1 <= port_int <= 65535):
                raise ValueError('Port must be between 1 and 65535')
        except ValueError:
            raise ValueError('Port must be a valid integer')
        return v

    class Config:
        validate_assignment = True
        extra = 'forbid'  # Запрещаем лишние поля
