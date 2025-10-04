import { useEffect, useRef } from 'react';
import type { MouseEvent } from 'react';

import { formatDuration } from '../utils/time';
import { resolveAssetPath } from '../utils/assets';

interface FinalResultModalProps {
  visible: boolean;
  moves: number;
  secondsElapsed: number;
  players: Array<{ id: number; score: number }>;
  matchedAnimalsCount: number;
  translate: (key: string, options?: Record<string, unknown>) => string;
  onClose: () => void;
  onRestart: () => void;
}

export function FinalResultModal({
  visible,
  moves,
  secondsElapsed,
  players,
  matchedAnimalsCount,
  translate,
  onClose,
  onRestart,
}: FinalResultModalProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (!visible) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        event.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [visible, onClose]);

  useEffect(() => {
    const video = videoRef.current;
    if (!video || !visible) return;

    let rafId: number;
    let hasStopped = false;

    const checkTime = () => {
      if (!video.duration || hasStopped) return;
      
      if (video.currentTime >= video.duration - 0.3) {
        video.currentTime = video.duration - 0.3;
        video.pause();
        hasStopped = true;
      } else if (!video.paused) {
        rafId = requestAnimationFrame(checkTime);
      }
    };

    const handlePlay = () => {
      hasStopped = false;
      rafId = requestAnimationFrame(checkTime);
    };

    const handleLoadedMetadata = () => {
      if (video.duration) {
        rafId = requestAnimationFrame(checkTime);
      }
    };

    video.addEventListener('play', handlePlay);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);

    // Start checking if video is already loaded
    if (video.readyState >= 1) {
      rafId = requestAnimationFrame(checkTime);
    }

    return () => {
      if (rafId) {
        cancelAnimationFrame(rafId);
      }
      video.removeEventListener('play', handlePlay);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
    };
  }, [visible]);

  if (!visible) {
    return null;
  }

  const videoSrc = resolveAssetPath('assets/graphics/Realistic_lion_standing_202510040825.mp4');

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

  const handleInnerClick = (event: MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  return (
    <div
      className="final-result-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby="final-result-title"
      onClick={onClose}
    >
      <div className="final-result-modal__card" role="document" onClick={handleInnerClick}>
        {videoSrc && (
          <div className="final-result-modal__video">
            <video 
              ref={videoRef} 
              autoPlay 
              muted 
              playsInline
            >
              <source src={videoSrc} type="video/mp4" />
            </video>
          </div>
        )}
        
        <div className="final-result-modal__body">
          <h2 id="final-result-title">{translate('completion.title')}</h2>
          <p className="final-result-modal__subtitle">{translate('completion.subtitle')}</p>
          
          {winnerMessage && (
            <p className="final-result-modal__winner">{winnerMessage}</p>
          )}

          <div className="final-result-modal__stats">
            <div className="final-result-modal__stat-item">
              <span className="final-result-modal__stat-label">{translate('stats.moves')}</span>
              <span className="final-result-modal__stat-value">{moves}</span>
            </div>
            <div className="final-result-modal__stat-item">
              <span className="final-result-modal__stat-label">{translate('stats.time')}</span>
              <span className="final-result-modal__stat-value">{formatDuration(secondsElapsed)}</span>
            </div>
            <div className="final-result-modal__stat-item">
              <span className="final-result-modal__stat-label">{translate('stats.matches')}</span>
              <span className="final-result-modal__stat-value">{matchedAnimalsCount}</span>
            </div>
          </div>

          {players.length > 1 && (
            <div className="final-result-modal__players">
              <h3>{translate('stats.playerScores')}</h3>
              <ul>
                {players.map((player) => (
                  <li key={player.id}>
                    <span>{translate('stats.playerName', { index: player.id + 1 })}</span>
                    <span>{translate('stats.pairs', { count: player.score })}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="final-result-modal__actions">
            <button type="button" className="primary" onClick={onRestart}>
              {translate('controls.restart')}
            </button>
            <button type="button" className="ghost" onClick={onClose}>
              {translate('game.continue')}
            </button>
          </div>
        </div>
      </div>
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
