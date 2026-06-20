"""
CRUD-операции для пользователя.

Слой между роутерами и БД. Роутеры не пишут SQL напрямую —
они вызывают эти функции. Это упрощает тестирование и поддержку.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Найти пользователя по email (или None)."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    """Найти пользователя по id (или None)."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Создать нового пользователя.
    Пароль хешируется перед сохранением — в БД попадает только хеш.
    """
    user = User(
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        full_name=user_in.full_name,
        timezone=user_in.timezone,
    )
    db.add(user)
    await db.flush()       # получаем id, не закрывая транзакцию
    await db.refresh(user)
    return user
