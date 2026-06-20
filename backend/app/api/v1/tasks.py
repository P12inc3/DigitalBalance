"""
Роутер «Задачи (To-Do)».

Все эндпоинты защищены: требуют авторизации и работают только
с записями текущего пользователя.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud import secretary as crud
from app.database import get_db
from app.models.user import User
from app.schemas.secretary import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать задачу."""
    return await crud.create_task(db, current_user.id, data)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список всех задач: невыполненные сверху."""
    return await crud.get_tasks(db, current_user.id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить одну задачу по id."""
    task = await crud.get_task(db, current_user.id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Частично обновить задачу (например, отметить выполненной)."""
    task = await crud.update_task(db, current_user.id, task_id, data)
    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить задачу."""
    deleted = await crud.delete_task(db, current_user.id, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Задача не найдена")
