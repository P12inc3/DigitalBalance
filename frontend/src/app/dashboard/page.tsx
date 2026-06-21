"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  getMe,
  getTasks,
  createTask,
  updateTask,
  deleteTask,
  getEvents,
  clearToken,
  getToken,
  type User,
  type Task,
  type EventItem,
} from "@/lib/api";
import { EventsPanel } from "@/components/EventsPanel";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [events, setEvents] = useState<EventItem[]>([]);
  const [newTask, setNewTask] = useState("");
  const [loading, setLoading] = useState(true);
  const [adding, setAdding] = useState(false);

  // Загрузка данных при входе на страницу.
  const loadData = useCallback(async () => {
    try {
      const [me, taskList, eventList] = await Promise.all([
        getMe(),
        getTasks(),
        getEvents(),
      ]);
      setUser(me);
      setTasks(taskList);
      setEvents(eventList);
    } catch {
      // Токен невалиден или отсутствует — на страницу входа.
      clearToken();
      router.push("/login");
    } finally {
      setLoading(false);
    }
  }, [router]);

  useEffect(() => {
    // Нет токена — сразу на логин, не дёргаем API.
    if (!getToken()) {
      router.push("/login");
      return;
    }
    loadData();
  }, [loadData, router]);

  async function handleAddTask() {
    const title = newTask.trim();
    if (!title) return;
    setAdding(true);
    try {
      const task = await createTask(title);
      setTasks((prev) => [task, ...prev]);
      setNewTask("");
    } catch {
      // тихо игнорируем, можно добавить тост позже
    } finally {
      setAdding(false);
    }
  }

  async function handleToggle(task: Task) {
    // Оптимистично обновляем UI, потом синхронизируем с сервером.
    setTasks((prev) =>
      prev.map((t) => (t.id === task.id ? { ...t, is_done: !t.is_done } : t))
    );
    try {
      await updateTask(task.id, { is_done: !task.is_done });
    } catch {
      // откат при ошибке
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, is_done: task.is_done } : t))
      );
    }
  }

  async function handleDelete(id: number) {
    const prev = tasks;
    setTasks((cur) => cur.filter((t) => t.id !== id));
    try {
      await deleteTask(id);
    } catch {
      setTasks(prev); // откат
    }
  }

  function handleLogout() {
    clearToken();
    router.push("/login");
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center">
        <p className="font-mono text-sm text-ink-faint">Загрузка...</p>
      </main>
    );
  }

  const doneCount = tasks.filter((t) => t.is_done).length;

  return (
    <main className="min-h-screen">
      {/* Шапка */}
      <header className="border-b border-base-700">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-2">
            <div className="h-2.5 w-2.5 rounded-full bg-accent" />
            <span className="font-mono text-sm text-ink-muted">
              digital balance
            </span>
          </div>
          <button
            onClick={handleLogout}
            className="text-sm text-ink-faint transition-colors hover:text-ink-muted"
          >
            Выйти
          </button>
        </div>
      </header>

      <div className="mx-auto max-w-3xl px-6 py-10">
        {/* Приветствие */}
        <p className="font-mono text-sm text-accent">
          {new Date().toLocaleDateString("ru-RU", {
            weekday: "long",
            day: "numeric",
            month: "long",
          })}
        </p>
        <h1 className="mt-2 text-3xl font-semibold text-ink">
          Привет, {user?.full_name}
        </h1>

        {/* Сводка по задачам — данные как в дашборде */}
        <div className="mt-8 flex gap-px overflow-hidden rounded-xl border border-base-700 bg-base-700">
          <div className="flex-1 bg-base-800 p-5">
            <div className="font-mono text-3xl text-ink">{tasks.length}</div>
            <div className="mt-1 text-sm text-ink-faint">всего задач</div>
          </div>
          <div className="flex-1 bg-base-800 p-5">
            <div className="font-mono text-3xl text-accent">{doneCount}</div>
            <div className="mt-1 text-sm text-ink-faint">выполнено</div>
          </div>
          <div className="flex-1 bg-base-800 p-5">
            <div className="font-mono text-3xl text-ember">
              {tasks.length - doneCount}
            </div>
            <div className="mt-1 text-sm text-ink-faint">осталось</div>
          </div>
        </div>

        {/* Две колонки: задачи слева, календарь справа */}
        <div className="mt-10 grid grid-cols-1 gap-10 lg:grid-cols-2">
          {/* ── Колонка задач ── */}
          <div>
            <h2 className="mb-4 text-lg font-medium text-ink">Задачи</h2>

            {/* Добавление задачи */}
            <div className="flex gap-3">
              <input
                type="text"
                value={newTask}
                onChange={(e) => setNewTask(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddTask()}
                placeholder="Новая задача..."
                className="flex-1 rounded-lg border border-base-600 bg-base-800 px-4 py-2.5 text-ink placeholder:text-ink-faint focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent"
              />
              <button
                onClick={handleAddTask}
                disabled={adding}
                className="rounded-lg bg-accent px-5 py-2.5 font-medium text-base-900 transition-colors hover:bg-accent-hover disabled:opacity-50"
              >
                Добавить
              </button>
            </div>

            {/* Список задач */}
            <div className="mt-6 space-y-2">
          {tasks.length === 0 ? (
            <div className="rounded-xl border border-dashed border-base-600 py-12 text-center">
              <p className="text-ink-muted">Пока нет задач</p>
              <p className="mt-1 text-sm text-ink-faint">
                Добавь первую — начни день с малого
              </p>
            </div>
          ) : (
            tasks.map((task) => (
              <div
                key={task.id}
                className="group flex items-center gap-3 rounded-lg border border-base-700 bg-base-800 px-4 py-3 transition-colors hover:border-base-600"
              >
                <button
                  onClick={() => handleToggle(task)}
                  className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-md border transition-colors ${
                    task.is_done
                      ? "border-accent bg-accent text-base-900"
                      : "border-base-600 hover:border-accent"
                  }`}
                  aria-label={task.is_done ? "Снять отметку" : "Выполнить"}
                >
                  {task.is_done && (
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 12 12"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M10 3L4.5 8.5L2 6"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                  )}
                </button>

                <span
                  className={`flex-1 ${
                    task.is_done
                      ? "text-ink-faint line-through"
                      : "text-ink"
                  }`}
                >
                  {task.title}
                </span>

                {task.priority === "high" && !task.is_done && (
                  <span className="rounded bg-ember-dim/40 px-2 py-0.5 font-mono text-xs text-ember">
                    важно
                  </span>
                )}

                <button
                  onClick={() => handleDelete(task.id)}
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

          {/* ── Колонка календаря ── */}
          <EventsPanel events={events} onEventsChange={setEvents} />
        </div>
      </div>
    </main>
  );
}
