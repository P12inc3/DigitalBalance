import type { Metadata } from "next";
import { Inter, JetBrains_Mono } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin", "cyrillic"],
  variable: "--font-sans",
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "Цифровой Баланс",
    template: "%s · Цифровой Баланс",
  },
  description: "Lifespace · Персональный цифровой ментор и секретарь для управления качеством жизни",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Инлайн-скрипт применяет сохранённую тему ДО отрисовки —
  // это устраняет «вспышку» неправильной темы при загрузке страницы.
  const themeScript = `
    (function() {
      try {
        var t = localStorage.getItem('db_theme') || 'dark';
        document.documentElement.classList.add(t);
      } catch (e) {
        document.documentElement.classList.add('dark');
      }
    })();
  `;

  return (
    <html lang="ru" className={`${inter.variable} ${jetbrainsMono.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{ __html: themeScript }} />
      </head>
      <body>{children}</body>
    </html>
  );
}
