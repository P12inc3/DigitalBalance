import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Цвета ссылаются на CSS-переменные (определены в globals.css).
        // Значения переменных меняются в зависимости от темы (тёмная/светлая),
        // поэтому существующие классы (bg-base-900 и т.д.) работают в обеих темах.
        base: {
          900: "var(--c-base-900)", // основной фон страницы
          800: "var(--c-base-800)", // карточки, панели
          700: "var(--c-base-700)", // границы по умолчанию
          600: "var(--c-base-600)", // активные/ховер границы
        },
        accent: {
          DEFAULT: "var(--c-accent)",
          hover: "var(--c-accent-hover)",
          dim: "var(--c-accent-dim)",
        },
        ember: {
          DEFAULT: "var(--c-ember)",
          dim: "var(--c-ember-dim)",
        },
        ink: {
          DEFAULT: "var(--c-ink)",     // основной текст
          muted: "var(--c-ink-muted)", // вторичный
          faint: "var(--c-ink-faint)", // подписи
        },
      },
      fontFamily: {
        sans: ["var(--font-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-mono)", "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};

export default config;
