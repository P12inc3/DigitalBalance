"""
Модели модуля «Умный секретарь»: события (Event) и задачи (Task).
Обе сущности привязаны к пользователю через user_id — это гарантирует
изоляцию данных между пользователями.
"""
import enum
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskPriority(str, enum.Enum):
    """Приоритет задачи."""
    low = "low"
    medium = "medium"
    high = "high"


class Event(Base):
    """Событие в календаре: встреча, рабочий блок, напоминание."""
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    start_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    end_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Тип события: meeting (встреча), work_block (рабочий блок), reminder (напоминание)
    event_type: Mapped[str] = mapped_column(
        String(50), default="meeting", nullable=False
    )
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} title={self.title!r} user_id={self.user_id}>"


class Task(Base):
    """Задача в to-do листе."""
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    is_done: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    priority: Mapped[TaskPriority] = mapped_column(
        Enum(TaskPriority), default=TaskPriority.medium, nullable=False
    )
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} done={self.is_done}>"
