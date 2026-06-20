"""
CRUD-операции модуля «Секретарь».

КЛЮЧЕВОЙ ПРИНЦИП БЕЗОПАСНОСТИ: каждая операция фильтрует записи по user_id.
Пользователь не может получить, изменить или удалить чужую запись — запрос
с чужим id вернёт None (то есть 404), а не данные другого человека.
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.secretary import Event, Task
from app.schemas.secretary import (
    EventCreate,
    EventUpdate,
    TaskCreate,
    TaskUpdate,
)


# ──────────────────────────── EVENT ────────────────────────────

async def create_event(db: AsyncSession, user_id: int, data: EventCreate) -> Event:
    event = Event(user_id=user_id, **data.model_dump())
    db.add(event)
    await db.flush()
    await db.refresh(event)
    return event


async def get_events(db: AsyncSession, user_id: int) -> list[Event]:
    """Все события пользователя, отсортированные по времени начала."""
    result = await db.execute(
        select(Event).where(Event.user_id == user_id).order_by(Event.start_time)
    )
    return list(result.scalars().all())


async def get_event(db: AsyncSession, user_id: int, event_id: int) -> Event | None:
    """Одно событие — только если оно принадлежит этому пользователю."""
    result = await db.execute(
        select(Event).where(Event.id == event_id, Event.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_event(
    db: AsyncSession, user_id: int, event_id: int, data: EventUpdate
) -> Event | None:
    event = await get_event(db, user_id, event_id)
    if event is None:
        return None
    # exclude_unset=True — обновляем только реально переданные поля.
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    await db.flush()
    await db.refresh(event)
    return event


async def delete_event(db: AsyncSession, user_id: int, event_id: int) -> bool:
    event = await get_event(db, user_id, event_id)
    if event is None:
        return False
    await db.delete(event)
    await db.flush()
    return True


# ──────────────────────────── TASK ────────────────────────────

async def create_task(db: AsyncSession, user_id: int, data: TaskCreate) -> Task:
    task = Task(user_id=user_id, **data.model_dump())
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_tasks(db: AsyncSession, user_id: int) -> list[Task]:
    """Все задачи пользователя: сначала невыполненные, потом по дате создания."""
    result = await db.execute(
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.is_done, Task.created_at.desc())
    )
    return list(result.scalars().all())


async def get_task(db: AsyncSession, user_id: int, task_id: int) -> Task | None:
    """Одна задача — только если она принадлежит этому пользователю."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_task(
    db: AsyncSession, user_id: int, task_id: int, data: TaskUpdate
) -> Task | None:
    task = await get_task(db, user_id, task_id)
    if task is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, user_id: int, task_id: int) -> bool:
    task = await get_task(db, user_id, task_id)
    if task is None:
        return False
    await db.delete(task)
    await db.flush()
    return True
