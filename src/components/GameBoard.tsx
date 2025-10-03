import type { AnimalEntry, CardData } from '../types';
import { PLACEHOLDER_IMAGE, resolveAssetPath } from '../utils/assets';

interface GameBoardProps {
  cards: CardData[];
  animalsById: Record<string, AnimalEntry>;
  onCardClick: (cardId: string) => void;
  isInteractive: boolean;
  translate: (key: string, options?: Record<string, unknown>) => string;
  gridSize: number;
}

export function GameBoard({ cards, animalsById, onCardClick, isInteractive, translate, gridSize }: GameBoardProps) {
  if (cards.length === 0) {
    return (
      <section className="board board--empty">
        <p>{translate('game.waitingForStart')}</p>
      </section>
    );
  }

  return (
    <section className="board" data-grid-size={gridSize}>
      {cards.map((card) => {
        const animal = animalsById[card.animalId];
        if (!animal) {
          return null;
        }
        const revealed = card.revealed || card.matched;
        const disabled = card.matched || card.revealed || !isInteractive;
        const imageSrc = resolveAssetPath(animal.image) || PLACEHOLDER_IMAGE;
        const groupKey = (animal.group || '').toLowerCase();
        const backIconSrc = groupKey ? resolveAssetPath(`assets/icons/${groupKey}.png`) : '';
        return (
          <button
            key={card.id}
            type="button"
            className={
              'memory-card' +
              (revealed ? ' is-revealed' : '') +
              (card.matched ? ' is-matched' : '')
            }
            onClick={() => onCardClick(card.id)}
            disabled={disabled}
            aria-pressed={revealed}
          >
            {revealed ? (
              <div className="memory-card__content">
                <div className="memory-card__image">
                  <img src={imageSrc} alt={animal.commonName} loading="lazy" />
                </div>
                <h3 className="memory-card__name">{animal.commonName}</h3>
              </div>
            ) : (
              <div className="memory-card__back" data-group={animal.group}>
                {backIconSrc ? (
                  <img className="memory-card__back-image" src={backIconSrc} alt={animal.group ? `${animal.group} icon` : translate('game.tapToReveal')} loading="lazy" />
                ) : (
                  <span className="memory-card__back-label">{translate('game.tapToReveal')}</span>
                )}
              </div>
            )}
          </button>
        );
      })}
    </section>
  );
}
