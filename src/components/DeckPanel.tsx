import type { AnimalEntry } from '../types';

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
  const imageSrc = current && current.image && current.image.trim() ? current.image : '/assets/placeholder.svg';

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
            <img src={imageSrc} alt={current.commonName} loading="lazy" />
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
