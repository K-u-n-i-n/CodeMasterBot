import os
from pathlib import Path

from dotenv import load_dotenv

# ============================================================================
# Поэтапная миграция на Dynaconf с fallback к существующим настройкам
# ============================================================================

# DYNACONF INTEGRATION (Enterprise Configuration Management)

# Настройка ALLOWED_HOSTS с резервным механизмом
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF_TRUSTED_ORIGINS - обработка пустой строки
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_origins.split(',') if origin.strip()
]

try:
    from dynaconf import Dynaconf

    # Настройка Dynaconf для чтения конфигурации
    settings = Dynaconf(
        envvar_prefix='DYNACONF',
        environments=True,
        settings_files=[
            str(
                Path(__file__).resolve().parent.parent.parent
                / 'config'
                / 'settings.toml'
            ),
            str(
                Path(__file__).resolve().parent.parent.parent
                / 'config'
                / '.secrets.toml'
            ),
        ],
        env_switcher='ENV_FOR_DYNACONF',
        load_dotenv=True,  # Сохраняем совместимость с .env
    )

    # Функция для получения настройки с fallback
    def get_config(key, default=None, env_var=None):
        """Получить настройку из Dynaconf с fallback к переменным окружения"""
        try:
            return getattr(settings, key, os.getenv(env_var or key, default))
        except AttributeError:
            # settings объект недоступен
            return os.getenv(env_var or key, default)

    DYNACONF_ENABLED = True

except ImportError:
    # Fallback если Dynaconf не установлен
    load_dotenv()

    def get_config(key, default=None, env_var=None):
        """Fallback к переменным окружения"""
        return os.getenv(env_var or key, default)

    DYNACONF_ENABLED = False

# ============================================================================
# DJANGO SETTINGS (с поддержкой Dynaconf)
# ============================================================================

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_FAKE_TOKEN = os.getenv('TELEGRAM_FAKE_TOKEN')

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# CSRF_TRUSTED_ORIGINS - обработка пустой строки
csrf_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in csrf_origins.split(',') if origin.strip()
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'bot.apps.BotConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'backend.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Используем Dynaconf для выбора БД (SQLite для локальной разработки)
if DYNACONF_ENABLED:
    # Читаем настройки БД из Dynaconf
    db_engine = get_config('DATABASE_ENGINE', 'django.db.backends.sqlite3')

    if db_engine == 'django.db.backends.sqlite3':
        # SQLite для локальной разработки
        db_name = get_config('DATABASE_NAME', BASE_DIR / 'db.sqlite3')
        DATABASES = {
            'default': {
                'ENGINE': db_engine,
                'NAME': db_name,
            }
        }
    else:
        # PostgreSQL для тестового/продакшен сервера
        DATABASES = {
            'default': {
                'ENGINE': db_engine,
                'NAME': get_config(
                    'DATABASE_NAME', os.getenv('POSTGRES_DB', 'postgres')
                ),
                'USER': get_config(
                    'DATABASE_USER', os.getenv('POSTGRES_USER', 'postgres')
                ),
                'PASSWORD': get_config(
                    'DATABASE_PASSWORD',
                    os.getenv('POSTGRES_PASSWORD', 'postgres'),
                ),
                'HOST': get_config(
                    'DATABASE_HOST', os.getenv('POSTGRES_HOST', 'localhost')
                ),
                'PORT': get_config(
                    'DATABASE_PORT', os.getenv('POSTGRES_PORT', '5432')
                ),
            }
        }
else:
    # Fallback: если Dynaconf не работает, используем SQLite
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = Path(BASE_DIR).joinpath('staticfiles').resolve()
STATICFILES_DIRS = (BASE_DIR / 'static',)

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(BASE_DIR).joinpath('media').resolve()

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'bot.CustomUser'
