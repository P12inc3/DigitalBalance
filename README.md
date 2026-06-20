# Digital Balance — Backend

API для портала «Цифровой Баланс» на FastAPI.

## Стек
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** (async) — ORM
- **PostgreSQL** / **SQLite** — БД (SQLite по умолчанию для разработки)
- **JWT** + **bcrypt** — авторизация и безопасность

## Запуск (локально)

1. Установить зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Создать `.env` из шаблона:
   ```bash
   cp .env.example .env
   ```
   (По умолчанию используется SQLite — поднимать Postgres не нужно.)

3. Запустить сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

4. Проверить:
   - API: http://localhost:8000
   - Swagger-документация: http://localhost:8000/docs

## Структура

```
app/
├── main.py        # точка входа, подключение роутеров
├── config.py      # настройки из .env
├── database.py    # подключение к БД, async-сессии
├── models/        # ORM-модели (таблицы БД)
├── schemas/       # Pydantic-схемы (валидация запросов/ответов)
├── api/v1/        # роутеры по модулям
├── core/          # бизнес-логика и безопасность
└── crud/          # операции с БД
```

## Переход на PostgreSQL

Заменить в `.env`:
```
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/digital_balance
```
