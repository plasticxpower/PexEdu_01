import type { AnimalEntry } from '../types';
import { PLACEHOLDER_IMAGE, buildResponsiveAsset, resolveAssetPath } from '../utils/assets';

interface DeckPanelProps {
  animals: AnimalEntry[];
  currentIndex: number;
  onPrev: () => void;
  onNext: () => void;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

export function DeckPanel({ animals, currentIndex, onPrev, onNext, translate }: DeckPanelProps) {
  const hasCards = animals.length > 0;
  const current = hasCards ? animals[currentIndex] : null;
  const deckImageAsset = current ? buildResponsiveAsset(current.image) : null;
  const deckImageFallback =
    deckImageAsset?.fallback || resolveAssetPath(current?.image) || PLACEHOLDER_IMAGE;
  const deckImageSources = deckImageAsset?.sources ?? [];
  const deckImageSizes = '(max-width: 768px) 90vw, (max-width: 1280px) 45vw, 420px';

  return (
    <section className="deck">
      <div className="deck__header">
        <h2>{translate('deck.title')}</h2>
        <span className="deck__count">
          {translate('deck.counter', { current: hasCards ? currentIndex + 1 : 0, total: animals.length })}
        </span>
      </div>
      {hasCards && current ? (
        <div className="deck__content">
          <div className="deck__image">
            <button
              type="button"
              className="deck__arrow deck__arrow--prev"
              onClick={onPrev}
              disabled={!hasCards || currentIndex === 0}
              aria-label={translate('deck.prev')}
            >
              &#8592;
            </button>
            <picture>
              {deckImageSources.map((source) => (
                <source
                  key={source.type}
                  type={source.type}
                  srcSet={source.srcSet}
                  sizes={deckImageSizes}
                />
              ))}
              <img
                src={deckImageFallback}
                alt={current.commonName}
                loading="lazy"
                width={400}
                height={200}
                decoding="async"
              />
            </picture>
            <button
              type="button"
              className="deck__arrow deck__arrow--next"
              onClick={onNext}
              disabled={!hasCards || currentIndex >= animals.length - 1}
              aria-label={translate('deck.next')}
            >
              &#8594;
            </button>
          </div>
          <div className="deck__details">
            <h3>{current.commonName}</h3>
            <p className="deck__scientific">{current.scientificName}</p>
            <ul>
              <li>
                <strong>{translate('game.attributes.size')}</strong>
                <span>{current.size}</span>
              </li>
              <li>
                <strong>{translate('game.attributes.lifespan')}</strong>
                <span>{current.lifeExpectancy}</span>
              </li>
              <li>
                <strong>{translate('game.attributes.habitat')}</strong>
                <span>{current.habitat}</span>
              </li>
              <li>
                <strong>{translate('game.attributes.funFact')}</strong>
                <span>{current.funFact}</span>
              </li>
            </ul>
          </div>
        </div>
      ) : (
        <p className="deck__empty">{translate('deck.empty')}</p>
      )}
    </section>
  );
}
