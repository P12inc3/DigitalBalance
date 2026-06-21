"""
Pydantic-схемы модуля «Генератор мотивации».
"""
from pydantic import BaseModel


class MotivationResponse(BaseModel):
    """Сводка мотивации для дашборда."""
    current_streak: int          # дней подряд сейчас
    longest_streak: int          # рекорд за всю историю
    total_active_days: int       # всего активных дней
    active_days_last_30: list[str]  # ISO-даты активности за 30 дней
    message: str                 # поддерживающее сообщение
