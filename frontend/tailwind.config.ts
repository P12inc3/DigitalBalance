import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        // Фон — глубокий сине-серый, «ночное небо»
        base: {
          900: "#0d1117", // основной фон страницы
          800: "#151b24", // карточки, панели
          700: "#1c2530", // границы по умолчанию
          600: "#2a3744", // активные/ховер границы
        },
        // Мятно-голубой акцент — спокойствие, баланс, основные действия
        accent: {
          DEFAULT: "#4ecdc4",
          hover: "#3db8af",
          dim: "#2a6b66",
        },
        // Янтарный — прогресс, стрики, «огонёк» мотивации
        ember: {
          DEFAULT: "#f0a868",
          dim: "#7a5638",
        },
        // Текст
        ink: {
          DEFAULT: "#e6edf3", // основной
          muted: "#8b98a5",   // вторичный
          faint: "#5a6671",   // подписи
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
