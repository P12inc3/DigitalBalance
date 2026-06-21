"""
Модели модуля «Архитектор здоровья».

Три сущности:
  WaterLog  — записи о выпитой воде (много за день)
  MealLog   — записи о приёмах пищи (много за день)
  DailyRoutine — настройка режима дня (ОДНА на пользователя)

Все привязаны к user_id — изоляция данных между пользователями.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class MealType(str, enum.Enum):
    """Тип приёма пищи."""
    breakfast = "breakfast"  # завтрак
    lunch = "lunch"          # обед
    dinner = "dinner"        # ужин
    snack = "snack"          # перекус


class WaterLog(Base):
    """Одна запись о выпитой воде (например, стакан 250 мл)."""
    __tablename__ = "water_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    amount_ml: Mapped[int] = mapped_column(Integer, nullable=False)

    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<WaterLog id={self.id} amount={self.amount_ml}ml>"


class MealLog(Base):
    """Одна запись о приёме пищи."""
    __tablename__ = "meal_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    meal_type: Mapped[MealType] = mapped_column(
        Enum(MealType), default=MealType.snack, nullable=False
    )

    logged_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<MealLog id={self.id} name={self.name!r} kcal={self.calories}>"


class DailyRoutine(Base):
    """
    Настройка режима дня. ОДНА запись на пользователя.
    Хранит время подъёма/сна и дневную цель по воде.
    Время храним строкой 'HH:MM' — этого достаточно для режима.
    """
    __tablename__ = "daily_routines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,  # одна настройка на юзера
        index=True,
        nullable=False,
    )

    wake_time: Mapped[str] = mapped_column(String(5), default="07:00", nullable=False)
    sleep_time: Mapped[str] = mapped_column(String(5), default="23:00", nullable=False)

    # Дневная цель по воде в мл (по умолчанию 2000 мл).
    water_goal_ml: Mapped[int] = mapped_column(Integer, default=2000, nullable=False)

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<DailyRoutine user_id={self.user_id} goal={self.water_goal_ml}ml>"
