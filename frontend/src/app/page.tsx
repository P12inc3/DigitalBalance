import Link from "next/link";
import { ThemeToggle } from "@/components/ThemeToggle";

export default function Home() {
  return (
    <main className="relative min-h-screen overflow-hidden">
      {/* Атмосферный градиент — «ночное небо», чистый CSS без внешних ассетов */}
      <div
        className="pointer-events-none absolute inset-0 opacity-60"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% -10%, rgba(78,205,196,0.12), transparent 60%), radial-gradient(ellipse 60% 40% at 80% 110%, rgba(240,168,104,0.08), transparent 60%)",
        }}
      />

      <div className="relative mx-auto flex min-h-screen max-w-5xl flex-col px-6">
        {/* Шапка */}
        <header className="flex items-center justify-between py-6">
          <div className="flex items-center gap-2">
            <div className="h-3 w-3 rounded-full bg-accent" />
            <span className="font-mono text-sm tracking-wide text-ink-muted">
              digital balance
            </span>
          </div>
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link
              href="/login"
              className="text-sm text-ink-muted transition-colors hover:text-ink"
            >
              Войти
            </Link>
          </div>
        </header>

        {/* Главный экран */}
        <div className="flex flex-1 flex-col justify-center py-20">
          <p className="mb-4 font-mono text-sm text-accent">
            персональный ментор и секретарь
          </p>
          <h1 className="max-w-3xl text-5xl font-semibold leading-tight tracking-tight text-ink sm:text-6xl">
            Управляй качеством
            <br />
            своей жизни
          </h1>
          <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink-muted">
            Единое защищённое пространство: календарь и задачи, режим дня,
            трекеры здоровья и прогресс — всё, что помогает держать баланс.
          </p>

          <div className="mt-10 flex flex-wrap items-center gap-4">
            <Link
              href="/register"
              className="rounded-lg bg-accent px-6 py-3 font-medium text-base-900 transition-colors hover:bg-accent-hover"
            >
              Начать
            </Link>
            <Link
              href="/login"
              className="rounded-lg border border-base-600 px-6 py-3 font-medium text-ink transition-colors hover:border-ink-faint"
            >
              У меня есть аккаунт
            </Link>
          </div>

          {/* Три опоры продукта — данные, а не декор */}
          <div className="mt-20 grid grid-cols-1 gap-px overflow-hidden rounded-xl border border-base-700 bg-base-700 sm:grid-cols-3">
            {[
              { num: "01", label: "Секретарь", desc: "календарь, задачи, встречи" },
              { num: "02", label: "Здоровье", desc: "режим, вода, питание" },
              { num: "03", label: "Прогресс", desc: "стрики и мотивация" },
            ].map((item) => (
              <div key={item.num} className="bg-base-800 p-6">
                <span className="font-mono text-xs text-accent">{item.num}</span>
                <h3 className="mt-3 font-medium text-ink">{item.label}</h3>
                <p className="mt-1 text-sm text-ink-faint">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        <footer className="py-6 font-mono text-xs text-ink-faint">
          MVP · Astana
        </footer>
      </div>
    </main>
  );
}
