"""
Роутер «Генератор мотивации».

Эндпоинт:
  GET /motivation/streaks — стрики, прогресс и поддерживающее сообщение
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.streaks import compute_streaks, get_motivation_message
from app.crud.health import get_today_summary
from app.database import get_db
from app.models.user import User
from app.schemas.motivation import MotivationResponse

router = APIRouter(prefix="/motivation", tags=["motivation"])


@router.get("/streaks", response_model=MotivationResponse)
async def get_streaks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Возвращает текущий и рекордный стрик, общее число активных дней,
    активность за 30 дней и поддерживающее сообщение.
    """
    today = datetime.now(timezone.utc).date()
    streaks = await compute_streaks(db, current_user.id, today)

    # Для сообщения учитываем ещё и прогресс по воде за сегодня.
    summary = await get_today_summary(db, current_user.id)
    message = get_motivation_message(
        streaks["current_streak"], summary["water_percent"]
    )

    return MotivationResponse(**streaks, message=message)
