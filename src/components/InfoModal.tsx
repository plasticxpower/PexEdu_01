import { useEffect, useId } from 'react';
import type { MouseEvent, ReactNode } from 'react';

interface InfoModalProps {
  visible: boolean;
  title: string;
  closeLabel: string;
  onClose: () => void;
  children: ReactNode;
}

export function InfoModal({ visible, title, closeLabel, onClose, children }: InfoModalProps) {
  const titleId = useId();

  useEffect(() => {
    if (!visible) {
      return;
    }

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

  if (!visible) {
    return null;
  }

  const handleInnerClick = (event: MouseEvent<HTMLDivElement>) => {
    event.stopPropagation();
  };

  return (
    <div className="info-modal" role="dialog" aria-modal="true" aria-labelledby={titleId} onClick={onClose}>
      <div className="info-modal__card" role="document" onClick={handleInnerClick}>
        <div className="info-modal__body">
          <h2 id={titleId}>{title}</h2>
          <div className="info-modal__content">{children}</div>
          <div className="info-modal__actions">
            <button type="button" className="primary" onClick={onClose}>
              {closeLabel}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
