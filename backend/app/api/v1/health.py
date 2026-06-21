"""
Роутер «Архитектор здоровья».

Группы эндпоинтов (все защищены авторизацией, работают только со своими данными):
  /health-tracker/water    — вода (POST добавить, GET список за сегодня, DELETE)
  /health-tracker/meals    — питание (POST, GET за сегодня, DELETE)
  /health-tracker/routine  — режим дня (GET, PUT сохранить)
  /health-tracker/summary  — сводка за сегодня
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.crud import health as crud
from app.database import get_db
from app.models.user import User
from app.schemas.health import (
    WaterCreate,
    WaterResponse,
    MealCreate,
    MealResponse,
    RoutineUpdate,
    RoutineResponse,
    HealthSummary,
)

router = APIRouter(prefix="/health-tracker", tags=["health"])


# ──────────────────────────── WATER ────────────────────────────

@router.post("/water", response_model=WaterResponse, status_code=status.HTTP_201_CREATED)
async def add_water(
    data: WaterCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Добавить запись о выпитой воде."""
    return await crud.add_water(db, current_user.id, data)


@router.get("/water", response_model=list[WaterResponse])
async def list_water(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Записи о воде за сегодня."""
    return await crud.get_water_logs(db, current_user.id)


@router.delete("/water/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_water(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить запись о воде."""
    ok = await crud.delete_water(db, current_user.id, log_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Запись не найдена")


# ──────────────────────────── MEALS ────────────────────────────

@router.post("/meals", response_model=MealResponse, status_code=status.HTTP_201_CREATED)
async def add_meal(
    data: MealCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Добавить приём пищи."""
    return await crud.add_meal(db, current_user.id, data)


@router.get("/meals", response_model=list[MealResponse])
async def list_meals(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Приёмы пищи за сегодня."""
    return await crud.get_meal_logs(db, current_user.id)


@router.delete("/meals/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Удалить приём пищи."""
    ok = await crud.delete_meal(db, current_user.id, meal_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Запись не найдена")


# ──────────────────────────── ROUTINE ────────────────────────────

@router.get("/routine", response_model=RoutineResponse)
async def get_routine(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить режим дня. Если ещё не настроен — создаём с дефолтами
    (подъём 07:00, сон 23:00, цель 2000 мл), чтобы фронт всегда имел данные.
    """
    routine = await crud.get_routine(db, current_user.id)
    if routine is None:
        routine = await crud.upsert_routine(db, current_user.id, RoutineUpdate())
    return routine


@router.put("/routine", response_model=RoutineResponse)
async def save_routine(
    data: RoutineUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сохранить настройки режима (создаёт или обновляет)."""
    return await crud.upsert_routine(db, current_user.id, data)


# ──────────────────────────── SUMMARY ────────────────────────────

@router.get("/summary", response_model=HealthSummary)
async def get_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сводка за сегодня: вода, цель, процент, калории, приёмы пищи."""
    return await crud.get_today_summary(db, current_user.id)
