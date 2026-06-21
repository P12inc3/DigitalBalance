"use client";

import { useState } from "react";
import {
  type EventItem,
  createEvent,
  deleteEvent,
} from "@/lib/api";

interface EventsPanelProps {
  events: EventItem[];
  onEventsChange: (events: EventItem[]) => void;
}

/** Форматирует ISO-строку в читаемое время: «21 июня, 14:00». */
function formatEventTime(iso: string): string {
  const d = new Date(iso);
  return d.toLocaleString("ru-RU", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Возвращает значение для input[type=datetime-local] на +1 час от текущего момента, округлённое. */
function defaultStart(): string {
  const d = new Date();
  d.setMinutes(0, 0, 0);
  d.setHours(d.getHours() + 1);
  // Формат YYYY-MM-DDTHH:mm для datetime-local (локальное время)
  const tzOffset = d.getTimezoneOffset() * 60000;
  return new Date(d.getTime() - tzOffset).toISOString().slice(0, 16);
}

export function EventsPanel({ events, onEventsChange }: EventsPanelProps) {
  const [title, setTitle] = useState("");
  const [startTime, setStartTime] = useState(defaultStart());
  const [adding, setAdding] = useState(false);
  const [error, setError] = useState("");

  async function handleAdd() {
    const trimmed = title.trim();
    if (!trimmed) return;
    setError("");
    setAdding(true);
    try {
      // Конец события — на час позже начала.
      const start = new Date(startTime);
      const end = new Date(start.getTime() + 60 * 60 * 1000);

      const event = await createEvent({
        title: trimmed,
        start_time: start.toISOString(),
        end_time: end.toISOString(),
        event_type: "meeting",
      });
      // Вставляем и сортируем по времени начала.
      const next = [...events, event].sort(
        (a, b) =>
          new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
      );
      onEventsChange(next);
      setTitle("");
      setStartTime(defaultStart());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Не удалось добавить");
    } finally {
      setAdding(false);
    }
  }

  async function handleDelete(id: number) {
    const prev = events;
    onEventsChange(events.filter((e) => e.id !== id));
    try {
      await deleteEvent(id);
    } catch {
      onEventsChange(prev); // откат при ошибке
    }
  }

  return (
    <div>
      <h2 className="mb-4 text-lg font-medium text-ink">Календарь</h2>

      {/* Добавление события */}
      <div className="space-y-2">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder="Название встречи..."
          className="w-full rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-ink placeholder:text-ink-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
        />
        <div className="flex gap-2">
          <input
            type="datetime-local"
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
            className="flex-1 rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-sm text-ink focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
          />
          <button
            onClick={handleAdd}
            disabled={adding}
            className="rounded-lg bg-accent px-5 py-2.5 font-medium text-base-900 transition-colors hover:bg-accent-hover disabled:opacity-50"
          >
            Добавить
          </button>
        </div>
        {error && <p className="text-sm text-red-400">{error}</p>}
      </div>

      {/* Список событий */}
      <div className="mt-6 space-y-2">
        {events.length === 0 ? (
          <div className="rounded-xl border border-dashed border-base-600 py-12 text-center">
            <p className="text-ink-muted">Нет запланированных встреч</p>
            <p className="mt-1 text-sm text-ink-faint">
              Добавь первую встречу или рабочий блок
            </p>
          </div>
        ) : (
          events.map((event) => (
            <div
              key={event.id}
              className="group flex items-start gap-3 rounded-lg border border-base-700 bg-base-800 px-4 py-3 transition-colors hover:border-base-600"
            >
              {/* Цветная метка слева */}
              <div className="mt-1.5 h-2 w-2 shrink-0 rounded-full bg-accent" />

              <div className="min-w-0 flex-1">
                <p className="truncate text-ink">{event.title}</p>
                <p className="mt-0.5 font-mono text-xs text-ink-faint">
                  {formatEventTime(event.start_time)}
                  {event.location && ` · ${event.location}`}
                </p>
              </div>

              <button
                onClick={() => handleDelete(event.id)}
                className="text-ink-faint opacity-0 transition-opacity hover:text-red-400 group-hover:opacity-100"
                aria-label="Удалить"
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 16 16"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                >
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
  );
}
