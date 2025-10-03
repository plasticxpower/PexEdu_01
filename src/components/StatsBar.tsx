import { formatDuration } from '../utils/time';

interface StatsBarProps {
  moves: number;
  secondsElapsed: number;
  isComplete: boolean;
  players: Array<{ id: number; score: number }>;
  currentPlayerIndex: number;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

export function StatsBar({ moves, secondsElapsed, isComplete, players, currentPlayerIndex, translate }: StatsBarProps) {
  const showPlayers = players.length > 1;
  const activePlayerLabel = translate('stats.playerName', { index: currentPlayerIndex + 1 });

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
      {showPlayers ? (
        <div className="stats__players">
          <strong>{translate('stats.players')}</strong>
          <ul className="stats__players-list">
            {players.map((player, index) => {
              const name = translate('stats.playerName', { index: index + 1 });
              const score = translate('stats.pairs', { count: player.score });
              const isActive = index === currentPlayerIndex && !isComplete;
              return (
                <li key={player.id} className={isActive ? 'active' : undefined}>
                  <span className="stats__players-name">{name}</span>
                  <span className="stats__players-score">{score}</span>
                </li>
              );
            })}
          </ul>
          {!isComplete ? (
            <div className="stats__turn">{translate('stats.currentTurn', { player: activePlayerLabel })}</div>
          ) : null}
        </div>
      ) : null}
    </section>
  );
}

