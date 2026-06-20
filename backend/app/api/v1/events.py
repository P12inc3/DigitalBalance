"""
Роутер «События календаря».

Все эндпоинты защищены: требуют авторизации и работают только
с записями текущего пользователя.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud import secretary as crud
from app.database import get_db
from app.models.user import User
from app.schemas.secretary import EventCreate, EventResponse, EventUpdate

router = APIRouter(prefix="/events", tags=["events"])


@router.post("", response_model=EventResponse, status_code=status.HTTP_201_CREATED)
async def create_event(
    data: EventCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать событие."""
    return await crud.create_event(db, current_user.id, data)


@router.get("", response_model=list[EventResponse])
async def list_events(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список всех событий текущего пользователя."""
    return await crud.get_events(db, current_user.id)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить одно событие по id."""
    event = await crud.get_event(db, current_user.id, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.patch("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: int,
    data: EventUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Частично обновить событие."""
    event = await crud.update_event(db, current_user.id, event_id, data)
    if event is None:
        raise HTTPException(status_code=404, detail="Событие не найдено")
    return event


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить событие."""
    deleted = await crud.delete_event(db, current_user.id, event_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Событие не найдено")
