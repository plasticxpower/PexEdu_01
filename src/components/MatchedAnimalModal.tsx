import { useEffect } from 'react';
import type { MouseEvent } from 'react';

import type { AnimalEntry } from '../types';
import { PLACEHOLDER_IMAGE, resolveAssetPath } from '../utils/assets';

interface MatchedAnimalModalProps {
  animal: AnimalEntry;
  onClose: () => void;
  translate: (key: string, options?: Record<string, unknown>) => string;
}

export function MatchedAnimalModal({ animal, onClose, translate }: MatchedAnimalModalProps) {
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' || event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  const imageSrc = resolveAssetPath(animal.image) || PLACEHOLDER_IMAGE;
  const labelId = `matched-animal-${animal.id}`;

  const handleInnerClick = (event: MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  return (
    <div
      className="animal-modal"
      role="dialog"
      aria-modal="true"
      aria-labelledby={labelId}
      onClick={onClose}
    >
      <div className="animal-modal__card" role="document" onClick={handleInnerClick}>
        <div className="animal-modal__image">
          <img src={imageSrc} alt={animal.commonName} loading="lazy" />
        </div>
        <div className="animal-modal__body">
          <h2 id={labelId}>{animal.commonName}</h2>
          <p className="animal-modal__scientific">{animal.scientificName}</p>
          <dl className="animal-modal__details">
            <div>
              <dt>{translate('game.attributes.size')}</dt>
              <dd>{animal.size}</dd>
            </div>
            <div>
              <dt>{translate('game.attributes.lifespan')}</dt>
              <dd>{animal.lifeExpectancy}</dd>
            </div>
            <div>
              <dt>{translate('game.attributes.habitat')}</dt>
              <dd>{animal.habitat}</dd>
            </div>
            <div>
              <dt>{translate('game.attributes.funFact')}</dt>
              <dd>{animal.funFact}</dd>
            </div>
          </dl>
          <button type="button" className="primary" onClick={onClose}>
            {translate('game.continue')}
          </button>
        </div>
      </div>
    </div>
  );
}
