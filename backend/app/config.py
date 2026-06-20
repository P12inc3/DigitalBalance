"""
Конфигурация приложения.
Все настройки читаются из переменных окружения (.env файл).
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Основное ---
    PROJECT_NAME: str = "Digital Balance API"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- База данных ---
    # По умолчанию SQLite для быстрого старта без поднятия Postgres.
    # Для продакшна заменить на:
    # postgresql+asyncpg://user:password@localhost:5432/digital_balance
    DATABASE_URL: str = "sqlite+aiosqlite:///./digital_balance.db"

    # --- Безопасность / JWT ---
    # ВАЖНО: в продакшне сгенерировать ключ и хранить в .env, не в коде!
    # Сгенерировать можно: openssl rand -hex 32
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    # Адрес фронтенда (Next.js dev server)
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]


@lru_cache
def get_settings() -> Settings:
    """Кэшированный синглтон настроек."""
    return Settings()


settings = get_settings()
