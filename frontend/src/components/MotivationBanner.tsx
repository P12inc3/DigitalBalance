"use client";

import { useEffect, useState } from "react";
import { type Motivation, getMotivation } from "@/lib/api";

/** Иконка огня — символ стрика. */
function FlameIcon({ active }: { active: boolean }) {
  return (
    <svg
      width="40"
      height="40"
      viewBox="0 0 24 24"
      fill="none"
      className={active ? "text-ember" : "text-ink-faint"}
    >
      <path
        d="M12 2c1 3 4 4.5 4 8a4 4 0 01-8 0c0-1 .3-1.8.7-2.5C8 8.5 7 9.5 7 12a5 5 0 0010 0c0-4.5-3.5-7-5-10z"
        fill="currentColor"
        opacity={active ? "1" : "0.4"}
      />
    </svg>
  );
}

/** Полоска активности за 30 дней — мини-календарь. */
function ActivityStrip({ activeDays }: { activeDays: string[] }) {
  const activeSet = new Set(activeDays);
  // Строим 30 дней от старого к новому (слева направо).
  const days: { date: string; active: boolean }[] = [];
  for (let i = 29; i >= 0; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const iso = d.toISOString().slice(0, 10);
    days.push({ date: iso, active: activeSet.has(iso) });
  }

  return (
    <div className="flex gap-1">
      {days.map((day) => (
        <div
          key={day.date}
          title={day.date}
          className={`h-6 flex-1 rounded-sm transition-colors ${
            day.active ? "bg-ember" : "bg-base-700"
          }`}
        />
      ))}
    </div>
  );
}

export function MotivationBanner() {
  const [data, setData] = useState<Motivation | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMotivation()
      .then(setData)
      .catch(() => {
        /* дашборд уже проверил авторизацию */
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading || !data) {
    return (
      <div className="rounded-xl border border-base-700 bg-base-800 p-6">
        <p className="font-mono text-sm text-ink-faint">Загрузка прогресса...</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-base-700 bg-base-800 p-6">
      {/* Верх: стрик + статистика */}
      <div className="flex flex-wrap items-center justify-between gap-6">
        <div className="flex items-center gap-4">
          <FlameIcon active={data.current_streak > 0} />
          <div>
            <div className="flex items-baseline gap-2">
              <span className="font-mono text-5xl text-ink">
                {data.current_streak}
              </span>
              <span className="text-ink-muted">
                {data.current_streak === 1 ? "день" : "дней"} подряд
              </span>
            </div>
            <p className="mt-1 text-sm text-ink-muted">{data.message}</p>
          </div>
        </div>

        {/* Рекорд и всего */}
        <div className="flex gap-6">
          <div className="text-center">
            <div className="font-mono text-2xl text-ember">
              {data.longest_streak}
            </div>
            <div className="mt-0.5 text-xs text-ink-faint">рекорд</div>
          </div>
          <div className="text-center">
            <div className="font-mono text-2xl text-accent">
              {data.total_active_days}
            </div>
            <div className="mt-0.5 text-xs text-ink-faint">всего дней</div>
          </div>
        </div>
      </div>

      {/* Полоска активности */}
      <div className="mt-6">
        <div className="mb-2 flex items-center justify-between">
          <span className="text-xs text-ink-faint">Активность за 30 дней</span>
        </div>
        <ActivityStrip activeDays={data.active_days_last_30} />
      </div>
    </div>
  );
}
