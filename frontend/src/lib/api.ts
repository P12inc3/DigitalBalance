/**
 * API-клиент для связи с бэкендом Digital Balance.
 *
 * Отвечает за:
 *  - хранение JWT-токена (в localStorage)
 *  - добавление токена в заголовки запросов
 *  - базовые методы для всех модулей
 */

// Адрес бэкенда. Меняется через переменную окружения NEXT_PUBLIC_API_URL.
const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const TOKEN_KEY = "db_access_token";

// ─────────────────────────── Токен ───────────────────────────

export function saveToken(token: string): void {
  if (typeof window !== "undefined") {
    localStorage.setItem(TOKEN_KEY, token);
  }
}

export function getToken(): string | null {
  if (typeof window !== "undefined") {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
}

export function clearToken(): void {
  if (typeof window !== "undefined") {
    localStorage.removeItem(TOKEN_KEY);
  }
}

// ─────────────────────────── Запросы ───────────────────────────

interface ApiError {
  detail: string | { msg: string }[];
}

/** Достаёт читаемый текст ошибки из ответа бэкенда. */
function extractError(data: ApiError): string {
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail) && data.detail[0]?.msg) {
    return data.detail[0].msg;
  }
  return "Что-то пошло не так";
}

/** Базовый запрос с автоматической подстановкой токена. */
async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers });

  // 204 No Content — тело пустое, парсить нечего.
  if (res.status === 204) {
    return undefined as T;
  }

  const data = await res.json();
  if (!res.ok) {
    throw new Error(extractError(data));
  }
  return data as T;
}

// ─────────────────────────── Auth ───────────────────────────

export interface User {
  id: number;
  email: string;
  full_name: string;
  timezone: string;
  created_at: string;
}

export async function register(
  email: string,
  password: string,
  full_name: string
): Promise<User> {
  return request<User>("/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name }),
  });
}

/** Логин использует form-data (требование OAuth2 на бэкенде). */
export async function login(email: string, password: string): Promise<string> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  const data = await res.json();
  if (!res.ok) {
    throw new Error(extractError(data));
  }
  saveToken(data.access_token);
  return data.access_token;
}

export async function getMe(): Promise<User> {
  return request<User>("/auth/me");
}

// ─────────────────────────── Tasks ───────────────────────────

export interface Task {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  is_done: boolean;
  priority: "low" | "medium" | "high";
  due_date: string | null;
  created_at: string;
}

export async function getTasks(): Promise<Task[]> {
  return request<Task[]>("/tasks");
}

export async function createTask(
  title: string,
  priority: "low" | "medium" | "high" = "medium"
): Promise<Task> {
  return request<Task>("/tasks", {
    method: "POST",
    body: JSON.stringify({ title, priority }),
  });
}

export async function updateTask(
  id: number,
  changes: Partial<Pick<Task, "is_done" | "title" | "priority">>
): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: "PATCH",
    body: JSON.stringify(changes),
  });
}

export async function deleteTask(id: number): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: "DELETE" });
}

// ─────────────────────────── Events ───────────────────────────

export interface EventItem {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string;
  event_type: string;
  location: string | null;
  created_at: string;
}

export interface EventCreateInput {
  title: string;
  start_time: string; // ISO-строка
  end_time: string;
  event_type?: string;
  location?: string;
}

export async function getEvents(): Promise<EventItem[]> {
  return request<EventItem[]>("/events");
}

export async function createEvent(
  data: EventCreateInput
): Promise<EventItem> {
  return request<EventItem>("/events", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteEvent(id: number): Promise<void> {
  return request<void>(`/events/${id}`, { method: "DELETE" });
}
