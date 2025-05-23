# Project.md

## 1. Описание проекта

Telegram-бот для проведения викторин с индивидуальными настройками, уведомлениями и возможностью расширения функционала. Бот работает в режиме Webhook, написан на Python с использованием python-telegram-bot. Проект частично реализован и деплоится на удалённый сервер. Архитектура учитывает масштабируемость, безопасность, резервное копирование и поддерживаемость.

## 2. Цели проекта
- Предоставить пользователям интерактивные викторины с индивидуальными настройками.
- Реализовать ежедневные уведомления о необходимости прохождения тестов.
- Обеспечить гибкость и расширяемость архитектуры для внедрения новых функций.
- Гарантировать безопасность и соответствие законодательству РФ по защите данных.

## 3. Архитектура
- **Язык:** Python 3.12
- **Фреймворк:** python-telegram-bot, Django 5.0.9
- **Веб-сервер:** Django (backend)
- **База данных:** PostgreSQL (с резервным копированием через pg_dump, cron, S3)
- **Очереди и события:** Redis, Celery (планируется)
- **WebSocket:** для событий в реальном времени (планируется)
- **Docker** для контейнеризации
- **CI/CD:** реализован на GitHub Actions
- **Мониторинг и логирование:** реализовать best practices (Sentry, Prometheus, логирование ошибок и бизнес-событий)

### 3.1. Основные компоненты
- Модуль Telegram-бота (обработка команд, логика викторины, взаимодействие с пользователем)
- Backend (Django): управление пользователями, настройками, статистикой, API
- Система уведомлений (ежедневные напоминания)
- Механизм хранения и расширения вопросов (в БД)
- Модуль статистики (планируется)
- Механизм поиска вопросов (планируется)
- Система резервного копирования и восстановления

## 4. Этапы разработки
1. MVP: базовый функционал бота, викторина, индивидуальные настройки, ежедневные уведомления (реализовано)
2. Расширение тем и базы вопросов (частично реализовано)
3. Интеграция Redis, Celery, WebSocket (в планах)
4. Реализация сбора и отображения статистики (в планах)
5. Поиск вопросов по названию (в планах)
6. UI/UX для отображения статистики, безопасность, оптимизация (в планах)

## 5. Используемые технологии
- Python==3.12
- Django==5.0.9
- python-telegram-bot==21.7
- Docker
- PostgreSQL
- Redis, Celery (планируется)
- WebSocket (планируется)
- Sentry, Prometheus (рекомендуется для мониторинга)
- Ruff (планируется) - универсальный линтер и форматтер кода
- UV (планируется) - быстрый менеджер Python-пакетов
- Dynaconf (планируется) - управление конфигурацией для различных сред

## 6. Стандарты и требования
- Чистота и читаемость кода (PEP8, docstrings)
- Безопасность хранения данных пользователей (шифрование, резервное копирование, соответствие законодательству РФ)
- Логирование и мониторинг ошибок и бизнес-событий
- Документирование архитектурных решений
- Поддерживаемость и расширяемость кода
- Единый стиль кодирования (Ruff для линтинга и форматирования)
- Управление конфигурацией через Dynaconf
- Эффективное управление зависимостями с UV
- Принципы SOLID, KISS, DRY, YAGNI

### Окружение разработки
- Windows 10 с WSL
- Python 3.12
- VS Code с расширением Ruff для линтинга и форматирования

### Стандарты кодирования
- Длина строки: максимум 79 символов (PEP 8)
- Кавычки: одинарные для строк, двойные для докстрингов
- Форматирование и линтинг через Ruff
- Автоматическая проверка через pre-commit hooks

## 7. Консистентность и поддерживаемость
- Все изменения архитектуры и функционала фиксируются в Project.md и Diary.md
- Ведение Tasktracker.md для отслеживания задач
- Регулярное обновление документации
- Все значимые шаги фиксируются в changelog.md

## 8. Диаграмма связей моделей

Вся актуальная ER-диаграмма моделей приложения представлена в файле [models_er_diagram.md](./models_er_diagram.md) в формате Mermaid.

- Диаграмма отражает все основные сущности, их поля, уникальные и внешние ключи, а также связи между моделями.
- При изменении моделей обязательно обновлять этот файл.

## 9. Планируемые улучшения инструментария

### Этап 1: Внедрение Ruff
- **Цель**: Замена flake8, isort, black на универсальный линтер/форматтер
- **Преимущества**: 
  - Значительное ускорение процессов линтинга и форматирования
  - Единая конфигурация вместо множества разрозненных
  - Расширенные возможности автоматического исправления
- **План внедрения**:
  - Настройка конфигурации в pyproject.toml
  - Обновление pre-commit hooks
  - Миграция CI/CD пайплайнов
  - Документирование правил и исключений

### Этап 2: Интеграция Dynaconf
- **Цель**: Изучение enterprise-подходов к управлению конфигурацией
- **Возможности**:
  - Поддержка множественных сред (dev, prod, test)
  - Безопасная работа с секретами
  - Валидация конфигурации через Pydantic
  - Гибкое переопределение настроек
- **Структура**:
  - settings.toml для основных настроек
  - .secrets.toml для чувствительных данных
  - validators.py для схем валидации
  - environments/ для конфигураций разных сред

### Этап 3: Переход на UV
- **Цель**: Модернизация управления зависимостями и виртуальными окружениями
- **Преимущества**:
  - Значительное ускорение установки пакетов
  - Улучшенная совместимость с современными Python-проектами
  - Встроенная поддержка кэширования и lockfile
  - Оптимизированная работа в CI/CD
- **Изменения**:
  - Обновление Dockerfile для использования UV
  - Миграция процесса установки зависимостей
  - Интеграция с существующими инструментами

---

_Документ обновляется при изменениях архитектуры или добавлении новых требований._
