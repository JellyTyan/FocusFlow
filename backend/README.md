# FocusFlow Backend

FastAPI сервер для приложения FocusFlow - системы продуктивного обучения с ИИ-помощником.

## 🏗 Архитектура

```
backend/
├── app/
│   ├── main.py              # Точка входа FastAPI
│   ├── models/              # Pydantic модели
│   │   ├── project.py       # Модели проектов
│   │   ├── topic.py         # Модели тем
│   │   └── session.py       # Модели сессий
│   ├── routers/             # API роутеры
│   │   ├── projects.py      # CRUD проектов
│   │   ├── topics.py        # CRUD тем
│   │   ├── sessions.py      # Управление сессиями
│   │   └── ai_chat.py       # ИИ-чат
│   ├── services/            # Бизнес-логика
│   │   ├── ai_service.py    # Интеграция с ИИ
│   │   ├── priority.py      # Расчет приоритетов
│   │   └── stats.py         # Статистика
│   └── database/            # База данных
│       ├── connection.py    # Подключение к БД
│       └── models.py        # SQLAlchemy модели
├── requirements.txt         # Зависимости
└── .env                     # Переменные окружения
```

## 📡 API Endpoints

### Проекты
- `GET /api/projects` - Список всех проектов
- `POST /api/projects` - Создать новый проект
- `GET /api/projects/{id}` - Получить проект по ID
- `PUT /api/projects/{id}` - Обновить проект
- `DELETE /api/projects/{id}` - Удалить проект

### Темы
- `GET /api/projects/{project_id}/topics` - Темы проекта
- `POST /api/projects/{project_id}/topics` - Добавить тему
- `PUT /api/topics/{id}` - Обновить тему (уверенность)
- `DELETE /api/topics/{id}` - Удалить тему
- `GET /api/topics/{id}/priority` - Рассчитать приоритет темы

### Сессии обучения
- `POST /api/sessions/start` - Начать сессию
- `PUT /api/sessions/{id}/pause` - Поставить на паузу
- `PUT /api/sessions/{id}/resume` - Возобновить
- `PUT /api/sessions/{id}/complete` - Завершить сессию
- `GET /api/sessions/{id}/status` - Статус сессии

### ИИ-чат
- `POST /api/chat/message` - Отправить сообщение ИИ
- `GET /api/chat/{session_id}/history` - История чата сессии
- `DELETE /api/chat/{session_id}` - Очистить историю

### Статистика
- `GET /api/stats/overview` - Общая статистика
- `GET /api/stats/projects/{id}` - Статистика проекта
- `GET /api/stats/stuck-topics` - Темы с частыми затруднениями

## 🗄 Модели данных

### Project
```python
{
    "id": "uuid",
    "name": "Экзамен по Биологии",
    "subject": "Биология", 
    "deadline": "2024-05-15",
    "created_at": "2024-01-15T10:00:00Z",
    "topics": [...],
    "progress": 0.6
}
```

### Topic
```python
{
    "id": "uuid",
    "project_id": "uuid",
    "name": "Фотосинтез",
    "confidence_level": 2,  # 1-5 звезд
    "priority_score": 8.5,
    "stuck_count": 3,       # Сколько раз застревал
    "created_at": "2024-01-15T10:00:00Z"
}
```

### Session
```python
{
    "id": "uuid",
    "topic_id": "uuid",
    "status": "active",     # active, paused, completed
    "start_time": "2024-01-15T10:00:00Z",
    "duration": 1500,       # секунды (25 мин)
    "stuck_moments": 2,     # Сколько раз нажал "Застрял"
    "completed": false
}
```

### ChatMessage
```python
{
    "id": "uuid",
    "session_id": "uuid",
    "role": "user",         # user, assistant
    "content": "Что такое цикл Кальвина?",
    "timestamp": "2024-01-15T10:05:00Z"
}
```

## 🤖 ИИ-интеграция

### Контекстный промпт
```python
system_prompt = f"""
Ты ИИ-помощник в приложении FocusFlow. 
Пользователь изучает тему: "{topic_name}" 
в рамках проекта: "{project_name}".

Твоя задача:
- Давать краткие, понятные объяснения
- Не отвлекать от учебы
- Мотивировать продолжать сессию
- Отвечать на русском языке

Пользователь застрял и нуждается в помощи.
"""
```

### Провайдеры ИИ
- **OpenAI GPT-4** (основной)
- **Google Gemini** (резервный)
- **Anthropic Claude** (опционально)

## 🔧 Сервисы

### PriorityService
Расчет приоритета тем по формуле:
```python
priority = (days_to_deadline ** -1) * (6 - confidence_level) * stuck_multiplier
```

### StatsService
- Подсчет завершенных сессий
- Анализ проблемных тем
- Расчет прогресса проекта

### AIService
- Управление контекстом чата
- Интеграция с API провайдеров
- Обработка ошибок ИИ

## 🚀 Запуск

### Установка зависимостей
```bash
pip install -r requirements.txt
```

### Переменные окружения (.env)
```env
DATABASE_URL=sqlite:///./focusflow.db
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
CORS_ORIGINS=http://localhost:3000
```

### Запуск сервера
```bash
uvicorn app.main:app --reload --port 8000
```

## 📊 База данных

### SQLite (для MVP)
- Простая настройка
- Файловая БД
- Подходит для прототипа

### Миграции
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 🔒 Безопасность

- CORS настройки для фронтенда
- Валидация входных данных (Pydantic)
- Ограничение запросов к ИИ API
- Санитизация пользовательского ввода

## 📈 Мониторинг

- Логирование запросов
- Метрики использования ИИ
- Отслеживание ошибок
- Время ответа API

## 🧪 Тестирование

```bash
pytest tests/
```

Покрытие:
- Unit тесты для сервисов
- Integration тесты для API
- Мок-тесты для ИИ интеграции

---

**Цель бэкенда**: Обеспечить быстрый, надежный API для фронтенда и эффективную интеграцию с ИИ-сервисами для контекстной помощи в обучении.