import { formatDuration } from '../utils/time';

interface StatsBarProps {
  moves: number;
  secondsElapsed: number;
  isComplete: boolean;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

export function StatsBar({ moves, secondsElapsed, isComplete, translate }: StatsBarProps) {
  return (
    <section className="stats" aria-live="polite">
      <div>
        <strong>{translate('stats.moves')}</strong>
        <span>{moves}</span>
      </div>
      <div>
        <strong>{translate('stats.time')}</strong>
        <span>{formatDuration(secondsElapsed)}</span>
      </div>
      {isComplete ? (
        <div className="stats__status">{translate('stats.completed')}</div>
      ) : null}
    </section>
  );
}
