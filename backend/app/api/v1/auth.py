"""
Роутер авторизации.

Эндпоинты:
  POST /register — регистрация
  POST /login    — вход (выдаёт пару токенов)
  POST /refresh  — обновление access-токена по refresh-токену
  GET  /me       — данные текущего пользователя (защищённый)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.crud.user import create_user, get_user_by_email
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    AccessToken,
    Token,
    TokenRefresh,
    UserCreate,
    UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Регистрация нового пользователя."""
    existing = await get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )
    user = await create_user(db, user_in)
    return user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Вход в систему.
    Поле username трактуется как email (требование стандарта OAuth2).
    Возвращает access + refresh токены.
    """
    user = await get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return Token(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=AccessToken)
async def refresh(body: TokenRefresh, db: AsyncSession = Depends(get_db)):
    """Выдать новый access-токен по действующему refresh-токену."""
    payload = decode_token(body.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh-токен",
        )
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh-токен",
        )
    return AccessToken(access_token=create_access_token(user_id))


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: User = Depends(get_current_user)):
    """Данные текущего авторизованного пользователя."""
    return current_user
