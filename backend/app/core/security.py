"""
Функции безопасности: хеширование паролей и JWT-токены.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config import settings


# --- Пароли ---
# bcrypt имеет архитектурный лимит: учитывает только первые 72 байта пароля.
# Поэтому перед хешированием обрезаем строку до 72 байт в кодировке UTF-8.
# Это стандартная практика, безопасность при этом не страдает.

def _to_72_bytes(password: str) -> bytes:
    """Кодирует пароль в UTF-8 и обрезает до лимита bcrypt в 72 байта."""
    return password.encode("utf-8")[:72]


def hash_password(plain_password: str) -> str:
    """Возвращает bcrypt-хеш пароля для хранения в БД."""
    hashed = bcrypt.hashpw(_to_72_bytes(plain_password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет, соответствует ли пароль сохранённому хешу."""
    return bcrypt.checkpw(
        _to_72_bytes(plain_password),
        hashed_password.encode("utf-8"),
    )


# --- JWT ---

def _create_token(subject: str | Any, expires_delta: timedelta, token_type: str) -> str:
    """Внутренний помощник: собирает и подписывает JWT."""
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": str(subject),      # обычно user_id
        "exp": expire,
        "type": token_type,       # "access" или "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: str | Any) -> str:
    """Короткоживущий токен для доступа к API."""
    return _create_token(
        subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access",
    )


def create_refresh_token(subject: str | Any) -> str:
    """Долгоживущий токен для обновления access-токена."""
    return _create_token(
        subject,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh",
    )


def decode_token(token: str) -> dict | None:
    """
    Декодирует и проверяет JWT.
    Возвращает payload при успехе или None, если токен невалиден/просрочен.
    """
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
