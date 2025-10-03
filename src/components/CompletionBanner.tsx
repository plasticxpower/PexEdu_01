import { formatDuration } from '../utils/time';

interface CompletionBannerProps {
  visible: boolean;
  moves: number;
  secondsElapsed: number;
  players: Array<{ id: number; score: number }>;
  translate: (key: string, options?: Record<string, unknown>) => string;
  onRestart: () => void;
}

export function CompletionBanner({ visible, moves, secondsElapsed, players, translate, onRestart }: CompletionBannerProps) {
  if (!visible) {
    return null;
  }

  let winnerMessage: string | null = null;
  if (players.length > 1) {
    const highestScore = Math.max(...players.map((player) => player.score), 0);
    const winners = players.filter((player) => player.score === highestScore);
    const pairsLabel = translate('stats.pairs', { count: highestScore });
    if (winners.length === 1) {
      const winnerName = translate('stats.playerName', { index: winners[0].id + 1 });
      winnerMessage = translate('completion.singleWinner', { player: winnerName, pairs: pairsLabel });
    } else {
      const winnerNames = winners.map((player) => translate('stats.playerName', { index: player.id + 1 }));
      const formattedNames = formatNamesList(winnerNames);
      if (winners.length === players.length) {
        winnerMessage = translate('completion.everyoneTie', { pairs: pairsLabel });
      } else {
        winnerMessage = translate('completion.sharedWin', { players: formattedNames, pairs: pairsLabel });
      }
    }
  }

  return (
    <div className="completion" role="status" aria-live="polite">
      <h2>{translate('completion.title')}</h2>
      <p>{translate('completion.subtitle')}</p>
      {winnerMessage ? <p className="completion__summary">{winnerMessage}</p> : null}
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

function formatNamesList(names: string[]): string {
  const ListFormat = (Intl as any)?.ListFormat;
  if (typeof ListFormat === 'function') {
    return new ListFormat(undefined, { style: 'long', type: 'conjunction' }).format(names);
  }
  if (names.length <= 1) {
    return names[0] ?? '';
  }
  if (names.length === 2) {
    return `${names[0]} and ${names[1]}`;
  }
  const head = names.slice(0, -1).join(', ');
  const last = names[names.length - 1];
  return `${head}, and ${last}`;
}
