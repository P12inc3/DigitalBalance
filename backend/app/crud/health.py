"""
CRUD-операции модуля «Архитектор здоровья».

Принцип безопасности тот же: всё фильтруется по user_id.
Особенности:
  - DailyRoutine: логика upsert (создать или обновить единственную запись)
  - get_today_summary: агрегация воды и калорий за текущий день
"""
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import WaterLog, MealLog, DailyRoutine
from app.schemas.health import WaterCreate, MealCreate, RoutineUpdate


# ──────────────────────────── WATER ────────────────────────────

async def add_water(db: AsyncSession, user_id: int, data: WaterCreate) -> WaterLog:
    log = WaterLog(user_id=user_id, amount_ml=data.amount_ml)
    db.add(log)
    await db.flush()
    await db.refresh(log)
    return log


async def get_water_logs(db: AsyncSession, user_id: int) -> list[WaterLog]:
    """Записи о воде за сегодня, новые сверху."""
    start = _today_start()
    result = await db.execute(
        select(WaterLog)
        .where(WaterLog.user_id == user_id, WaterLog.logged_at >= start)
        .order_by(WaterLog.logged_at.desc())
    )
    return list(result.scalars().all())


async def delete_water(db: AsyncSession, user_id: int, log_id: int) -> bool:
    result = await db.execute(
        select(WaterLog).where(WaterLog.id == log_id, WaterLog.user_id == user_id)
    )
    log = result.scalar_one_or_none()
    if log is None:
        return False
    await db.delete(log)
    await db.flush()
    return True


# ──────────────────────────── MEAL ────────────────────────────

async def add_meal(db: AsyncSession, user_id: int, data: MealCreate) -> MealLog:
    meal = MealLog(user_id=user_id, **data.model_dump())
    db.add(meal)
    await db.flush()
    await db.refresh(meal)
    return meal


async def get_meal_logs(db: AsyncSession, user_id: int) -> list[MealLog]:
    """Приёмы пищи за сегодня, новые сверху."""
    start = _today_start()
    result = await db.execute(
        select(MealLog)
        .where(MealLog.user_id == user_id, MealLog.logged_at >= start)
        .order_by(MealLog.logged_at.desc())
    )
    return list(result.scalars().all())


async def delete_meal(db: AsyncSession, user_id: int, meal_id: int) -> bool:
    result = await db.execute(
        select(MealLog).where(MealLog.id == meal_id, MealLog.user_id == user_id)
    )
    meal = result.scalar_one_or_none()
    if meal is None:
        return False
    await db.delete(meal)
    await db.flush()
    return True


# ──────────────────────────── ROUTINE ────────────────────────────

async def get_routine(db: AsyncSession, user_id: int) -> DailyRoutine | None:
    result = await db.execute(
        select(DailyRoutine).where(DailyRoutine.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def upsert_routine(
    db: AsyncSession, user_id: int, data: RoutineUpdate
) -> DailyRoutine:
    """
    Создаёт настройку режима, если её нет, иначе обновляет существующую.
    Так у пользователя всегда ровно одна запись режима.
    """
    routine = await get_routine(db, user_id)
    if routine is None:
        # Создаём с дефолтами, затем накатываем переданные поля.
        routine = DailyRoutine(user_id=user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(routine, field, value)
        db.add(routine)
    else:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(routine, field, value)
    await db.flush()
    await db.refresh(routine)
    return routine


# ──────────────────────── DAILY SUMMARY ────────────────────────

def _today_start() -> datetime:
    """Начало текущих суток в UTC."""
    now = datetime.now(timezone.utc)
    return now.replace(hour=0, minute=0, second=0, microsecond=0)


async def get_today_summary(db: AsyncSession, user_id: int) -> dict:
    """
    Считает за сегодня: сумму воды, цель по воде, процент,
    сумму калорий и число приёмов пищи.
    """
    start = _today_start()

    # Сумма воды за сегодня.
    water_result = await db.execute(
        select(func.coalesce(func.sum(WaterLog.amount_ml), 0)).where(
            WaterLog.user_id == user_id, WaterLog.logged_at >= start
        )
    )
    water_total = water_result.scalar() or 0

    # Сумма калорий и количество приёмов за сегодня.
    meal_result = await db.execute(
        select(
            func.coalesce(func.sum(MealLog.calories), 0),
            func.count(MealLog.id),
        ).where(MealLog.user_id == user_id, MealLog.logged_at >= start)
    )
    calories_total, meals_count = meal_result.one()

    # Цель по воде из режима (или дефолт 2000).
    routine = await get_routine(db, user_id)
    water_goal = routine.water_goal_ml if routine else 2000

    percent = round((water_total / water_goal) * 100) if water_goal > 0 else 0

    return {
        "water_total_ml": water_total,
        "water_goal_ml": water_goal,
        "water_percent": percent,
        "calories_total": calories_total or 0,
        "meals_count": meals_count or 0,
    }
