"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { register, login } from "@/lib/api";
import { InputField } from "@/components/InputField";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit() {
    setError("");
    if (!fullName || !email || !password) {
      setError("Заполни все поля");
      return;
    }
    if (password.length < 8) {
      setError("Пароль должен быть не короче 8 символов");
      return;
    }
    setLoading(true);
    try {
      await register(email, password, fullName);
      // Сразу логиним после регистрации — пользователь попадает в приложение.
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка регистрации");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <Link
          href="/"
          className="mb-8 inline-flex items-center gap-2 text-sm text-ink-faint transition-colors hover:text-ink-muted"
        >
          <div className="h-2.5 w-2.5 rounded-full bg-accent" />
          <span className="font-mono">digital balance</span>
        </Link>

        <h1 className="text-2xl font-semibold text-ink">Создать аккаунт</h1>
        <p className="mt-2 text-sm text-ink-muted">
          Первый шаг к балансу
        </p>

        <div className="mt-8 space-y-4">
          <InputField
            label="Имя"
            type="text"
            value={fullName}
            onChange={setFullName}
            placeholder="Как тебя зовут"
            autoComplete="name"
          />
          <InputField
            label="Email"
            type="email"
            value={email}
            onChange={setEmail}
            placeholder="you@example.com"
            autoComplete="email"
          />
          <InputField
            label="Пароль"
            type="password"
            value={password}
            onChange={setPassword}
            placeholder="минимум 8 символов"
            autoComplete="new-password"
          />

          {error && (
            <p className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-2.5 text-sm text-red-400">
              {error}
            </p>
          )}

          <button
            onClick={handleSubmit}
            disabled={loading}
            className="w-full rounded-lg bg-accent px-4 py-2.5 font-medium text-base-900 transition-colors hover:bg-accent-hover disabled:opacity-50"
          >
            {loading ? "Создаём..." : "Создать аккаунт"}
          </button>
        </div>

        <p className="mt-6 text-center text-sm text-ink-muted">
          Уже есть аккаунт?{" "}
          <Link href="/login" className="text-accent hover:text-accent-hover">
            Войти
          </Link>
        </p>
      </div>
    </main>
  );
}
