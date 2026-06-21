"""
Логика расчёта стриков («дней подряд с активностью»).

Принцип: стрик НЕ хранится в БД, а вычисляется из реальных дат активности.
Это исключает рассинхронизацию — счётчик всегда отражает правду.

«Активный день» = в этот день была хотя бы одна запись:
вода, приём пищи или выполненная/созданная задача.
"""
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.health import WaterLog, MealLog
from app.models.secretary import Task


async def _get_active_dates(db: AsyncSession, user_id: int) -> set[date]:
    """
    Собирает множество уникальных дат, в которые у пользователя была активность.
    Берём даты из логов воды, еды и задач.
    """
    active: set[date] = set()

    # Даты воды
    water_rows = await db.execute(
        select(WaterLog.logged_at).where(WaterLog.user_id == user_id)
    )
    for (dt,) in water_rows.all():
        active.add(dt.date())

    # Даты еды
    meal_rows = await db.execute(
        select(MealLog.logged_at).where(MealLog.user_id == user_id)
    )
    for (dt,) in meal_rows.all():
        active.add(dt.date())

    # Даты задач (по дате создания)
    task_rows = await db.execute(
        select(Task.created_at).where(Task.user_id == user_id)
    )
    for (dt,) in task_rows.all():
        active.add(dt.date())

    return active


def _calc_current_streak(active_dates: set[date], today: date) -> int:
    """
    Текущий стрик: непрерывная цепочка активных дней, идущая до сегодня.

    Стрик не рвётся, если сегодня активности ещё нет (день не закончился) —
    в этом случае отсчёт начинаем со вчера. Но если и вчера пусто — стрик 0.
    """
    if not active_dates:
        return 0

    # Точка отсчёта: сегодня, если есть активность, иначе вчера.
    if today in active_dates:
        cursor = today
    elif (today - timedelta(days=1)) in active_dates:
        cursor = today - timedelta(days=1)
    else:
        return 0

    streak = 0
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _calc_longest_streak(active_dates: set[date]) -> int:
    """Самая длинная непрерывная цепочка за всю историю."""
    if not active_dates:
        return 0

    longest = 0
    for d in active_dates:
        # Начало цепочки — день, перед которым нет активности.
        if (d - timedelta(days=1)) not in active_dates:
            length = 0
            cursor = d
            while cursor in active_dates:
                length += 1
                cursor += timedelta(days=1)
            longest = max(longest, length)
    return longest


async def compute_streaks(
    db: AsyncSession, user_id: int, today: date
) -> dict:
    """
    Главная функция: возвращает текущий и самый длинный стрик,
    общее число активных дней и список активных дат за последние 30 дней
    (для визуализации календаря активности на фронте).
    """
    active = await _get_active_dates(db, user_id)

    current = _calc_current_streak(active, today)
    longest = _calc_longest_streak(active)

    # Активность за последние 30 дней — для «тепловой» полоски на дашборде.
    last_30 = [
        (today - timedelta(days=i)).isoformat()
        for i in range(30)
        if (today - timedelta(days=i)) in active
    ]

    return {
        "current_streak": current,
        "longest_streak": longest,
        "total_active_days": len(active),
        "active_days_last_30": last_30,
    }


def get_motivation_message(current_streak: int, water_percent: int) -> str:
    """
    Подбирает поддерживающее сообщение по текущему состоянию.
    Без накрутки: сообщение честно отражает прогресс.
    """
    if current_streak == 0:
        return "Начни сегодня — один маленький шаг запускает цепочку."
    if current_streak == 1:
        return "Первый день засчитан. Завтра продолжи!"
    if current_streak < 7:
        return f"{current_streak} дней подряд. Ты набираешь обороты."
    if current_streak < 30:
        return f"{current_streak} дней! Это уже привычка, а не случайность."
    return f"{current_streak} дней — впечатляющая дисциплина. Так держать!"
