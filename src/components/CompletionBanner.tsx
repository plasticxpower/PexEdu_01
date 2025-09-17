import { formatDuration } from '../utils/time';

interface CompletionBannerProps {
  visible: boolean;
  moves: number;
  secondsElapsed: number;
  onRestart: () => void;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

export function CompletionBanner({ visible, moves, secondsElapsed, onRestart, translate }: CompletionBannerProps) {
  if (!visible) {
    return null;
  }

  return (
    <div className="completion" role="status" aria-live="polite">
      <h2>{translate('completion.title')}</h2>
      <p>{translate('completion.subtitle')}</p>
      <ul>
        <li>
          <strong>{translate('stats.moves')}</strong>
          <span>{moves}</span>
        </li>
        <li>
          <strong>{translate('stats.time')}</strong>
          <span>{formatDuration(secondsElapsed)}</span>
        </li>
      </ul>
      <button type="button" onClick={onRestart} className="primary">
        {translate('controls.restart')}
      </button>
    </div>
  );
}
