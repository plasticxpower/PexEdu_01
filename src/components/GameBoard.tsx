import type { AnimalEntry, CardData } from '../types';
import { PLACEHOLDER_IMAGE, buildResponsiveAsset, resolveAssetPath } from '../utils/assets';

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
        const groupKey = (animal.group || '').toLowerCase();
        const cardImageAsset = buildResponsiveAsset(animal.image);
        const cardImageFallback = cardImageAsset?.fallback || resolveAssetPath(animal.image) || PLACEHOLDER_IMAGE;
        const cardImageSources = cardImageAsset?.sources ?? [];

        const groupIconPath = groupKey ? `assets/icons/${groupKey}.png` : null;
        const backIconAsset = groupIconPath
          ? buildResponsiveAsset(groupIconPath, { widths: [256, 512], formats: ['webp'] })
          : null;
        const backIconFallback = groupIconPath
          ? backIconAsset?.fallback || resolveAssetPath(groupIconPath)
          : '';
        const backIconSources = backIconAsset?.sources ?? [];

        const cardImageSizes = '(max-width: 600px) 42vw, (max-width: 1200px) 24vw, 200px';
        const cardBackSizes = cardImageSizes;
        const trimmedName = animal.commonName?.trim() ?? '';
        const nameLength = trimmedName.length;
        const wordCount = trimmedName === '' ? 0 : trimmedName.split(/\s+/).length;
        let nameClassName = 'memory-card__name';
        if (nameLength > 26 || wordCount >= 4) {
          nameClassName += ' memory-card__name--xsmall';
        } else if (nameLength > 18 || wordCount >= 3) {
          nameClassName += ' memory-card__name--small';
        }
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
                  <picture>
                    {cardImageSources.map((source) => (
                      <source
                        key={source.type}
                        type={source.type}
                        srcSet={source.srcSet}
                        sizes={cardImageSizes}
                      />
                    ))}
                    <img
                      src={cardImageFallback}
                      alt={animal.commonName}
                      loading="lazy"
                      width={400}
                      height={300}
                      decoding="async"
                    />
                  </picture>
                </div>
                <h3 className={nameClassName}>{animal.commonName}</h3>
              </div>
            ) : (
              <div className="memory-card__back" data-group={animal.group}>
                {backIconFallback ? (
                  <picture>
                    {backIconSources.map((source) => (
                      <source
                        key={source.type}
                        type={source.type}
                        srcSet={source.srcSet}
                        sizes={cardBackSizes}
                      />
                    ))}
                    <img
                      className="memory-card__back-image"
                      src={backIconFallback}
                      alt={animal.group ? `${animal.group} icon` : translate('game.tapToReveal')}
                      loading="lazy"
                      width={256}
                      height={192}
                      decoding="async"
                    />
                  </picture>
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
