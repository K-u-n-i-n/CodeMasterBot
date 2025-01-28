# 🤖 CodeMasterBot

Этот проект представляет собой Telegram-бота, работающего в режиме Webhook.  
Бот написан на Python с использованием библиотеки [python-telegram-bot](https://docs.python-telegram-bot.org/en/v21.7/)  
Данный проект основан на этой [статье](https://yourtodo.life/ru/posts/django-5-s-botom-na-python-telegram-bot-213/) , код которой и был взят за основу для разработки бота на нижеописанном стеке.

---

**Что умеет бот:**

- Выдает 10 вопросов в виде викторины и проверяет правильность ответов
- Оповещает о необходимости пройти тесты (раз в сутки)  



**Что требуется реализовать в будущем:**

- Возможность поиска вопроса по названию
- Расширить перечень тем для викторины и наполнить бд по каждой из них
- Возможность настройки времени оповещения  для каждого пользователя
- Возможность выбора сложности (вида) тестов для каждого пользователя
- Возможность выбора темы викторины для каждого пользователя
- Реализовать сбор статистики пользователя для улучшения подачи вопросов
- Прикрутить к проекту Redis, Celery и подключить WebSocket для обработки событий в реальном времени.

---
Подробнее ознакомится с ходом работы можно в [релизах](https://github.com/K-u-n-i-n/CodeMasterBot/releases)  
Пощупать моего бота можно тут:  [CodeMasterBot](https://t.me/CodeMasterSuperBot)  




## 🚀 Основной функционал
- Работа в режиме Webhook.
- Подключение к PostgreSQL для хранения данных.
- Админ-панель на Django для управления контентом.
- Поддержка викторины (в данный момент без сохранения результатов пользователей).
- Логирование всех событий в файлы и в Docker.
- Автоматический деплой через GitHub Actions.





## Технологии:


![Python](https://img.shields.io/badge/Python-3.12.7-blue)
![Django](https://img.shields.io/badge/Django-5.0.9-green)
![python-telegram-bot](https://img.shields.io/badge/PythonTelegramBot-21.7-blue)

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-green)
![Docker](https://img.shields.io/badge/Docker-blue)

![Language](https://img.shields.io/badge/lang-ru-red)

## Особенности реализации
- Проект запускается в четырёх контейнерах — db, wsgi, bot и nginx;
- Образы masterbot_backend, masterbot_bot и masterbot_nginx запушены на DockerHub;
- Реализован workflow c автодеплоем (GitHub Actions) на удаленный сервер и отправкой сообщения в Telegram;

[![Main CodeMasterBot workflow](https://github.com/K-u-n-i-n/CodeMasterBot/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/K-u-n-i-n/CodeMasterBot/actions/workflows/main.yml)



## Развертывание на локальном сервере в режиме: Webhook
- [Зарегистрируйте Telegram бота](https://vc.ru/telegram/1552569-kak-sozdat-zaregistrirovat-telegram-bota)
- Узнайте ID своего телеграм-аккаунта. Необходимо для настройки оповещений (можно использовать для этого [бота](https://t.me/userinfobot))
- Создайте файл .env в корне проекта. Шаблон для заполнения файла находится в .env.example
- Установите [Docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/) 
- [Зарегистрируйтесь](https://dashboard.ngrok.com/get-started/setup/) и установите ngrok (если вы из России, то будут трудности...)
- Запустите Docker Desktop 
- Запустите ngrok для создания публичного URL (в терминале выполните команду для проброса порта 8443): `ngrok http 8443`
- Дополните файл .env адресом webhook который сгенерирует ngrok. Например: `WEBHOOK_URL=https://76fd-79-141-165-141.ngrok-free.app`
- Запустите docker compose, выполнив команду в терминале: `docker compose -f docker-compose.yml up --build -d`
- Выполните миграции: `docker compose -f docker-compose.yml exec wsgi python manage.py migrate`
- Создайте суперюзера: `docker compose -f docker-compose.yml exec wsgi python manage.py createsuperuser`
- Соберите статику: `docker compose -f docker-compose.yml exec wsgi python manage.py collectstatic --no-input`
- Зайдите в админку и создайте теги (тема: Функции, slug: func; тема: ..., slug: ...)
- Заполните базу вопросами: `docker compose -f docker-compose.yml exec wsgi python manage.py populate_questions`
- Бот готов к работе!


## <span style="color: red;">**ВАЖНО:**</span>  
Режим Webhook работает только при запущенном ngrok и при его перезапуске необходимо менять WEBHOOK_URL адрес в .env и делать рестарт контейнеров!

  
## Над проектом работали:
Python Developer: <span style="color: green;">*Кунин Александр*</span> (k.u.n.i.n@mail.ru)  
Manual QA Engineer: <span style="color: green;">*Татьяна Овчинникова*</span> (tg7110019@gmail.com)