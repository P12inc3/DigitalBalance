"""
Pydantic-схемы модуля «Архитектор здоровья».
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.health import MealType


# ──────────────────────────── WATER ────────────────────────────

class WaterCreate(BaseModel):
    amount_ml: int = Field(gt=0, le=5000, description="Объём в мл, 1–5000")


class WaterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    amount_ml: int
    logged_at: datetime


# ──────────────────────────── MEAL ────────────────────────────

class MealCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    calories: int | None = Field(default=None, ge=0, le=10000)
    meal_type: MealType = MealType.snack


class MealResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    calories: int | None
    meal_type: MealType
    logged_at: datetime


# ──────────────────────────── ROUTINE ────────────────────────────

class RoutineUpdate(BaseModel):
    """Все поля опциональны — обновляем только переданные."""
    wake_time: str | None = Field(
        default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="HH:MM"
    )
    sleep_time: str | None = Field(
        default=None, pattern=r"^([01]\d|2[0-3]):[0-5]\d$", description="HH:MM"
    )
    water_goal_ml: int | None = Field(default=None, gt=0, le=10000)


class RoutineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    wake_time: str
    sleep_time: str
    water_goal_ml: int
    updated_at: datetime


# ──────────────────────── DAILY SUMMARY ────────────────────────

class HealthSummary(BaseModel):
    """Сводка за сегодня — для дашборда здоровья."""
    water_total_ml: int
    water_goal_ml: int
    water_percent: int  # процент выполнения цели по воде (0–100+)
    calories_total: int
    meals_count: int
