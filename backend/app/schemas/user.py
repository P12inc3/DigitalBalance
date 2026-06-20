"""
Pydantic-схемы для пользователя и аутентификации.

Схемы определяют, какие данные принимает API на вход
и какие отдаёт на выход. Пароль НИКОГДА не возвращается клиенту.
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Регистрация / создание ---

class UserCreate(BaseModel):
    """Данные для регистрации нового пользователя."""
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=255)
    timezone: str = Field(default="UTC", max_length=64)


# --- Вход ---

class UserLogin(BaseModel):
    """Данные для входа."""
    email: EmailStr
    password: str


# --- Ответ клиенту ---

class UserResponse(BaseModel):
    """Публичные данные пользователя (без пароля)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    timezone: str
    created_at: datetime


# --- Токены ---

class Token(BaseModel):
    """Пара токенов, выдаётся при логине/регистрации."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenRefresh(BaseModel):
    """Запрос на обновление access-токена."""
    refresh_token: str


class AccessToken(BaseModel):
    """Ответ при обновлении — только новый access-токен."""
    access_token: str
    token_type: str = "bearer"
