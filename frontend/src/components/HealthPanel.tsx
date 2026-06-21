"use client";

import { useEffect, useState, useCallback } from "react";
import {
  type WaterLog,
  type MealLog,
  type Routine,
  type HealthSummary,
  getWaterToday,
  addWater,
  getMealsToday,
  addMeal,
  deleteMeal,
  getRoutine,
  saveRoutine,
  getHealthSummary,
} from "@/lib/api";
import { ProgressRing } from "@/components/ProgressRing";

const MEAL_LABELS: Record<MealLog["meal_type"], string> = {
  breakfast: "Завтрак",
  lunch: "Обед",
  dinner: "Ужин",
  snack: "Перекус",
};

export function HealthPanel() {
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [meals, setMeals] = useState<MealLog[]>([]);
  const [routine, setRoutine] = useState<Routine | null>(null);
  const [loading, setLoading] = useState(true);

  // Поля формы питания
  const [mealName, setMealName] = useState("");
  const [mealCalories, setMealCalories] = useState("");
  const [mealType, setMealType] = useState<MealLog["meal_type"]>("snack");

  // Поля формы режима
  const [wakeTime, setWakeTime] = useState("07:00");
  const [sleepTime, setSleepTime] = useState("23:00");
  const [waterGoal, setWaterGoal] = useState("2000");
  const [routineSaved, setRoutineSaved] = useState(false);

  const loadHealth = useCallback(async () => {
    try {
      const [s, m, r] = await Promise.all([
        getHealthSummary(),
        getMealsToday(),
        getRoutine(),
      ]);
      setSummary(s);
      setMeals(m);
      setRoutine(r);
      setWakeTime(r.wake_time);
      setSleepTime(r.sleep_time);
      setWaterGoal(String(r.water_goal_ml));
    } catch {
      // молча — дашборд уже проверил авторизацию
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadHealth();
  }, [loadHealth]);

  // Обновляем сводку после изменений воды/еды.
  async function refreshSummary() {
    try {
      setSummary(await getHealthSummary());
    } catch {
      /* no-op */
    }
  }

  async function handleAddWater(ml: number) {
    try {
      await addWater(ml);
      await refreshSummary();
    } catch {
      /* no-op */
    }
  }

  async function handleAddMeal() {
    const name = mealName.trim();
    if (!name) return;
    try {
      const cal = mealCalories ? parseInt(mealCalories, 10) : null;
      const meal = await addMeal(name, Number.isNaN(cal!) ? null : cal, mealType);
      setMeals((prev) => [meal, ...prev]);
      setMealName("");
      setMealCalories("");
      await refreshSummary();
    } catch {
      /* no-op */
    }
  }

  async function handleDeleteMeal(id: number) {
    const prev = meals;
    setMeals((cur) => cur.filter((m) => m.id !== id));
    try {
      await deleteMeal(id);
      await refreshSummary();
    } catch {
      setMeals(prev);
    }
  }

  async function handleSaveRoutine() {
    try {
      const r = await saveRoutine({
        wake_time: wakeTime,
        sleep_time: sleepTime,
        water_goal_ml: parseInt(waterGoal, 10) || 2000,
      });
      setRoutine(r);
      setRoutineSaved(true);
      setTimeout(() => setRoutineSaved(false), 2000);
      await refreshSummary();
    } catch {
      /* no-op */
    }
  }

  if (loading) {
    return (
      <p className="font-mono text-sm text-ink-faint">Загрузка здоровья...</p>
    );
  }

  return (
    <div>
      <h2 className="mb-6 text-lg font-medium text-ink">Здоровье</h2>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* ── Вода ── */}
        <div className="rounded-xl border border-base-700 bg-base-800 p-6">
          <h3 className="mb-4 text-sm font-medium text-ink-muted">
            Водный баланс
          </h3>
          <div className="flex items-center gap-6">
            {summary && (
              <ProgressRing
                percent={summary.water_percent}
                current={summary.water_total_ml}
                goal={summary.water_goal_ml}
              />
            )}
            <div className="flex flex-1 flex-col gap-2">
              <button
                onClick={() => handleAddWater(250)}
                className="rounded-lg border border-base-600 bg-base-700 px-4 py-2 text-sm text-ink transition-colors hover:border-accent"
              >
                + Стакан (250 мл)
              </button>
              <button
                onClick={() => handleAddWater(500)}
                className="rounded-lg border border-base-600 bg-base-700 px-4 py-2 text-sm text-ink transition-colors hover:border-accent"
              >
                + Бутылка (500 мл)
              </button>
            </div>
          </div>
        </div>

        {/* ── Калории (сводка) ── */}
        <div className="rounded-xl border border-base-700 bg-base-800 p-6">
          <h3 className="mb-4 text-sm font-medium text-ink-muted">
            Сегодня съедено
          </h3>
          <div className="flex items-baseline gap-2">
            <span className="font-mono text-4xl text-ember">
              {summary?.calories_total ?? 0}
            </span>
            <span className="text-ink-faint">ккал</span>
          </div>
          <p className="mt-2 text-sm text-ink-faint">
            {summary?.meals_count ?? 0} приёмов пищи
          </p>
        </div>
      </div>

      {/* ── Добавить приём пищи ── */}
      <div className="mt-6">
        <div className="flex flex-wrap gap-2">
          <input
            type="text"
            value={mealName}
            onChange={(e) => setMealName(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddMeal()}
            placeholder="Что съел..."
            className="min-w-[160px] flex-1 rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-ink placeholder:text-ink-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <input
            type="number"
            value={mealCalories}
            onChange={(e) => setMealCalories(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleAddMeal()}
            placeholder="ккал"
            className="w-24 rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-ink placeholder:text-ink-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <select
            value={mealType}
            onChange={(e) =>
              setMealType(e.target.value as MealLog["meal_type"])
            }
            className="rounded-lg border border-base-600 bg-base-800 px-3 py-2.5 text-ink focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          >
            <option value="breakfast">Завтрак</option>
            <option value="lunch">Обед</option>
            <option value="dinner">Ужин</option>
            <option value="snack">Перекус</option>
          </select>
          <button
            onClick={handleAddMeal}
            className="rounded-lg bg-accent px-5 py-2.5 font-medium text-base-900 transition-colors hover:bg-accent-hover"
          >
            Добавить
          </button>
        </div>

        {/* Список съеденного */}
        <div className="mt-4 space-y-2">
          {meals.length === 0 ? (
            <p className="py-4 text-center text-sm text-ink-faint">
              Сегодня ещё ничего не записано
            </p>
          ) : (
            meals.map((meal) => (
              <div
                key={meal.id}
                className="group flex items-center gap-3 rounded-lg border border-base-700 bg-base-800 px-4 py-2.5"
              >
                <span className="font-mono text-xs text-ink-faint">
                  {MEAL_LABELS[meal.meal_type]}
                </span>
                <span className="flex-1 text-ink">{meal.name}</span>
                {meal.calories != null && (
                  <span className="font-mono text-sm text-ember">
                    {meal.calories} ккал
                  </span>
                )}
                <button
                  onClick={() => handleDeleteMeal(meal.id)}
                  className="text-ink-faint opacity-0 transition-opacity hover:text-red-400 group-hover:opacity-100"
                  aria-label="Удалить"
                >
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path
                      d="M3 4h10M6.5 4V3a1 1 0 011-1h1a1 1 0 011 1v1m1.5 0v9a1 1 0 01-1 1H5a1 1 0 01-1-1V4"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* ── Режим дня ── */}
      <div className="mt-6 rounded-xl border border-base-700 bg-base-800 p-6">
        <h3 className="mb-4 text-sm font-medium text-ink-muted">Режим дня</h3>
        <div className="flex flex-wrap items-end gap-4">
          <label className="block">
            <span className="mb-1.5 block text-xs text-ink-faint">Подъём</span>
            <input
              type="time"
              value={wakeTime}
              onChange={(e) => setWakeTime(e.target.value)}
              className="rounded-lg border border-base-600 bg-base-700 px-3 py-2 text-ink focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-xs text-ink-faint">Отбой</span>
            <input
              type="time"
              value={sleepTime}
              onChange={(e) => setSleepTime(e.target.value)}
              className="rounded-lg border border-base-600 bg-base-700 px-3 py-2 text-ink focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </label>
          <label className="block">
            <span className="mb-1.5 block text-xs text-ink-faint">
              Цель воды, мл
            </span>
            <input
              type="number"
              value={waterGoal}
              onChange={(e) => setWaterGoal(e.target.value)}
              className="w-28 rounded-lg border border-base-600 bg-base-700 px-3 py-2 text-ink focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
            />
          </label>
          <button
            onClick={handleSaveRoutine}
            className="rounded-lg bg-accent px-5 py-2 font-medium text-base-900 transition-colors hover:bg-accent-hover"
          >
            {routineSaved ? "Сохранено ✓" : "Сохранить"}
          </button>
        </div>
      </div>
    </div>
  );
}
