"""
Точка входа приложения Digital Balance API.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine

# Импорт моделей обязателен до create_all — иначе SQLAlchemy
# не узнает о таблицах. Новые модели добавлять сюда.
from app.models import user  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Действия при старте и остановке приложения.

    На старте создаём таблицы из моделей напрямую (удобно для MVP/SQLite).
    Когда подключим Alembic, эту автогенерацию заменим миграциями.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Здесь можно закрывать ресурсы при остановке.


app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

# --- CORS: разрешаем фронтенду обращаться к API ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Базовые эндпоинты ---

@app.get("/")
async def root():
    """Корневой эндпоинт — проверка, что сервер жив."""
    return {
        "service": settings.PROJECT_NAME,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health-check для мониторинга."""
    return {"status": "healthy"}


# --- Роутеры модулей ---
from app.api.v1 import auth  # noqa: E402

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
