"""
Конфигурация приложения.
Все настройки читаются из переменных окружения (.env файл).
"""
from functools import lru_cache

from pydantic import field_validator
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
    # На проде (Railway) сюда придёт строка PostgreSQL — валидатор ниже
    # автоматически приведёт её к async-формату (postgresql+asyncpg://).
    DATABASE_URL: str = "sqlite+aiosqlite:///./digital_balance.db"

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        """
        Railway/Heroku выдают URL вида postgresql:// или postgres://.
        Наш async-движок требует драйвер asyncpg в схеме.
        Эта функция дописывает +asyncpg, если его нет.
        SQLite-строки не трогаются.
        """
        if v.startswith("postgresql+asyncpg://") or v.startswith("sqlite"):
            return v
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    # --- Безопасность / JWT ---
    # ВАЖНО: в продакшне сгенерировать ключ и хранить в .env, не в коде!
    # Сгенерировать можно: openssl rand -hex 32
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # --- CORS ---
    # Адреса фронтенда. Можно задать строкой через запятую в переменной
    # окружения, например: CORS_ORIGINS=https://app.vercel.app,http://localhost:3000
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_cors(cls, v):
        """Принимает либо список, либо строку с origin'ами через запятую."""
        if isinstance(v, str):
            # Если это JSON-массив — оставляем pydantic разобрать его сам.
            if v.strip().startswith("["):
                return v
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Кэшированный синглтон настроек."""
    return Settings()


settings = get_settings()
