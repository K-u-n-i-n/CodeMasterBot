/**
 * @file: models_er_diagram.md
 * @description: ER-диаграмма связей моделей Django-приложения (CustomUser, Tag, Question, UserSettings, UserQuestionStatistic)
 * @dependencies: backend/bot/models.py
 * @created: 2025-05-24
 */

---

```mermaid
erDiagram
    CUSTOMUSER {
        bigint user_id PK, UK "Telegram ID"
        string username
        string email
        string first_name
        string last_name
        string avatar
    }
    TAG {
        int id PK
        string name UK
        string slug UK
    }
    QUESTION {
        int id PK
        string name UK
        string description
        string syntax
    }
    USERSETTINGS {
        int id PK
        bigint user_id FK
        int tag_id FK
        string difficulty "default: easy"
        bool notification "default: False"
        time notification_time "default: 07:00"
    }
    USERQUESTIONSTATISTIC {
        int id PK
        bigint user_id FK
        int question_id FK
        int attempts "default: 0"
        int correct_attempts "default: 0"
        datetime last_attempt
        float rating "default: 0"
    }

    CUSTOMUSER ||--o{ USERSETTINGS : "имеет настройки"
    TAG ||--o{ USERSETTINGS : "используется в настройках"
    TAG }o--o{ QUESTION : "теги вопросов"
    CUSTOMUSER ||--o{ USERQUESTIONSTATISTIC : "статистика по вопросам"
    QUESTION ||--o{ USERQUESTIONSTATISTIC : "статистика пользователей"
```

---

_Диаграмма отражает все основные связи, уникальные и внешние ключи, а также типы и дефолты полей. Для актуализации — обновлять при изменении моделей._
