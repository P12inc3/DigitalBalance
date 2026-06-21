interface ProgressRingProps {
  percent: number; // 0..100+
  current: number; // мл выпито
  goal: number; // цель мл
}

/**
 * Кольцо прогресса на чистом SVG.
 * Заполняется по проценту, в центре — текущий объём.
 */
export function ProgressRing({ percent, current, goal }: ProgressRingProps) {
  const size = 140;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = 2 * Math.PI * radius;

  // Ограничиваем визуальное заполнение 100%, но цифру показываем реальную.
  const clamped = Math.min(percent, 100);
  const offset = circumference - (clamped / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center">
      <svg width={size} height={size} className="-rotate-90">
        {/* Фоновое кольцо */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#1c2530"
          strokeWidth={stroke}
        />
        {/* Заполнение */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="#4ecdc4"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-500"
        />
      </svg>
      {/* Центр */}
      <div className="absolute flex flex-col items-center">
        <span className="font-mono text-2xl text-ink">{percent}%</span>
        <span className="mt-0.5 font-mono text-xs text-ink-faint">
          {current}/{goal}
        </span>
      </div>
    </div>
  );
}
