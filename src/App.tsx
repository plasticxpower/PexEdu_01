import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import animalsJson from '../data/animals.json';
import csLocaleOverrides from '../data/animals.locale.cs.json';
import { CompletionBanner } from './components/CompletionBanner';
import { DeckPanel } from './components/DeckPanel';
import { FinalResultModal } from './components/FinalResultModal';
import { GameBoard } from './components/GameBoard';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { InfoModal } from './components/InfoModal';
import { MatchedAnimalModal } from './components/MatchedAnimalModal';
import { SettingsPanel } from './components/SettingsPanel';
import { StatsBar } from './components/StatsBar';
import { PLACEHOLDER_IMAGE, resolveAssetPath } from './utils/assets';
import { useGameEngine } from './hooks/useGameEngine';
import type { AnimalEntry, AnimalGroup, AnimalLocaleOverrides, GameSettings } from './types';

const DEFAULT_SETTINGS: GameSettings = {
  group: 'mammals',
  gridSize: 12,
  playerCount: 1,
};

const GROUPS: AnimalGroup[] = ['mammals', 'fish', 'amphibians', 'reptiles', 'birds'];

type ActiveView = 'menu' | 'game';
type SupportedLocale = 'en' | 'cs';

const LOCALE_OVERRIDES: Record<SupportedLocale, Record<string, AnimalLocaleOverrides>> = {
  en: {},
  cs: csLocaleOverrides as Record<string, AnimalLocaleOverrides>,
};

function resolveLocale(language: string): SupportedLocale {
  return language.startsWith('cs') ? 'cs' : 'en';
}

function localizeAnimal(animal: AnimalEntry, locale: SupportedLocale): AnimalEntry {
  const overrides = LOCALE_OVERRIDES[locale][animal.id];
  if (!overrides) {
    return animal;
  }
  const merged = {
    ...animal,
    ...overrides,
  };
  return {
    ...merged,
    image: resolveAssetPath(merged.image) || PLACEHOLDER_IMAGE,
  };
}

export default function App() {
  const { t, i18n } = useTranslation();
  const animals = useMemo(() => {
    return (animalsJson as AnimalEntry[]).map((animal) => ({
      ...animal,
      image: resolveAssetPath(animal.image) || PLACEHOLDER_IMAGE,
    }));
  }, []);
  const animalsById = useMemo(() => {
    return animals.reduce<Record<string, AnimalEntry>>((acc, animal) => {
      acc[animal.id] = animal;
      return acc;
    }, {});
  }, [animals]);
  const availableGroups = useMemo(
    () =>
      GROUPS.map((group) => ({
        group,
        count: animals.filter((animal) => animal.group === group).length,
      })),
    [animals]
  );

  const locale = resolveLocale(i18n.language);
  const localizedAnimalsById = useMemo(() => {
    return animals.reduce<Record<string, AnimalEntry>>((acc, animal) => {
      acc[animal.id] = localizeAnimal(animal, locale);
      return acc;
    }, {});
  }, [animals, locale]);

  const game = useGameEngine({ animals });
  const [settings, setSettings] = useState<GameSettings>(DEFAULT_SETTINGS);
  const [deckIndex, setDeckIndex] = useState(0);
  const previousMatchCount = useRef(0);
  const [view, setView] = useState<ActiveView>('menu');
  const [modalAnimalId, setModalAnimalId] = useState<string | null>(null);
  const [showFinalResult, setShowFinalResult] = useState(false);
  const [pendingFinalResult, setPendingFinalResult] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (game.isComplete) {
      setPendingFinalResult(true);
    } else {
      setPendingFinalResult(false);
      setShowFinalResult(false);
    }
  }, [game.isComplete]);


  useEffect(() => {
    const matches = game.matchedAnimals.length;
    if (matches === 0) {
      setDeckIndex(0);
      setModalAnimalId(null);
    } else if (matches > previousMatchCount.current) {
      setDeckIndex(matches - 1);
      const newestAnimal = game.matchedAnimals[matches - 1];
      if (newestAnimal) {
        setModalAnimalId(newestAnimal.id);
      }
    } else if (deckIndex >= matches) {
      setDeckIndex(Math.max(matches - 1, 0));
    }
    previousMatchCount.current = matches;
  }, [deckIndex, game.matchedAnimals]);

  useEffect(() => {
    // Pause timer when any overlay/modal is open, resume when closed
    if (modalAnimalId || isAboutOpen || isHelpOpen || isMenuOpen) {
      game.pauseTimer();
    } else if (game.isRunning && !game.isComplete) {
      game.resumeTimer();
    }
  }, [
    modalAnimalId,
    isAboutOpen,
    isHelpOpen,
    isMenuOpen,
    game.pauseTimer,
    game.resumeTimer,
    game.isRunning,
    game.isComplete,
  ]);

  const handleStart = () => {
    game.startGame(settings);
    setModalAnimalId(null);
    setShowFinalResult(false);
    setView('game');
  };

  const handleRestart = () => {
    setModalAnimalId(null);
    setShowFinalResult(false);
    game.restart();
  };

  const handleReturnToMenu = () => {
    game.reset();
    setDeckIndex(0);
    previousMatchCount.current = 0;
    setModalAnimalId(null);
    setShowFinalResult(false);
    setView('menu');
  };

  const handleCardClick = (cardId: string) => {
    if (modalAnimalId) {
      return;
    }
    game.revealCard(cardId);
  };

  const handlePrevDeck = () => {
    setDeckIndex((index) => Math.max(index - 1, 0));
  };

  const handleNextDeck = () => {
    setDeckIndex((index) => {
      const max = game.matchedAnimals.length - 1;
      return max < 0 ? 0 : Math.min(index + 1, max);
    });
  };

  const handleCloseModal = () => {
    setModalAnimalId(null);
    if (game.isComplete && pendingFinalResult) {
      window.setTimeout(() => {
        setShowFinalResult(true);
      }, 300);
      setPendingFinalResult(false);
    }
  };

  const handleCloseFinalResult = () => {
    setShowFinalResult(false);
  };

  useEffect(() => {
    if (!isMenuOpen) {
      return;
    }
    const handleClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsMenuOpen(false);
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClick);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClick);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isMenuOpen]);

  const handleToggleMenu = () => {
    setIsMenuOpen((open) => !open);
  };

  const handleOpenAbout = () => {
    setIsAboutOpen(true);
    setIsHelpOpen(false);
    setIsMenuOpen(false);
  };

  const handleOpenHelp = () => {
    setIsHelpOpen(true);
    setIsAboutOpen(false);
    setIsMenuOpen(false);
  };

  const hasActiveGame = game.activeSettings !== null;
  const isInteractive =
    game.isRunning && !game.isComplete && !modalAnimalId && !isAboutOpen && !isHelpOpen && !isMenuOpen;

  const localizedMatchedAnimals = useMemo(() => {
    return game.matchedAnimals.map((animal) => localizedAnimalsById[animal.id] ?? animal);
  }, [game.matchedAnimals, localizedAnimalsById]);

  const modalAnimal = modalAnimalId
    ? localizedAnimalsById[modalAnimalId] ?? animalsById[modalAnimalId]
    : null;

  const aboutParagraphs = t('info.about.paragraphs', { returnObjects: true }) as string[];
  const helpSteps = t('info.help.steps', { returnObjects: true }) as Array<{
    title: string;
    description: string;
  }>;
  const helpTips = t('info.help.tips', { returnObjects: true }) as string[];
  const helpIntro = t('info.help.intro');
  const helpTipsTitle = t('info.help.tipsTitle');
  const infoCloseLabel = t('info.close');

  return (
    <div className="app">
      <header className="app__header">
        <div className="app__header-toolbar">
          <LanguageSwitcher />
          <div className="app__menu" ref={menuRef}>
            <button
              type="button"
              className={`app__menu-toggle${isMenuOpen ? ' is-open' : ''}`}
              onClick={handleToggleMenu}
              aria-haspopup="menu"
              aria-expanded={isMenuOpen}
              aria-label={t('info.menuLabel')}
            >
              <span className="app__menu-icon" aria-hidden="true">
                <span />
                <span />
                <span />
              </span>
            </button>
            {isMenuOpen && (
              <div className="app__menu-dropdown" role="menu">
                <button type="button" className="app__menu-item" role="menuitem" onClick={handleOpenAbout}>
                  {t('info.about.button')}
                </button>
                <button type="button" className="app__menu-item" role="menuitem" onClick={handleOpenHelp}>
                  {t('info.help.button')}
                </button>
              </div>
            )}
          </div>
        </div>
        <div className="app__header-intro">
          <h1>{t('app.title')}</h1>
          <p>{t('app.description')}</p>
        </div>
      </header>

      <main className="app__main">
        {view === 'menu' ? (
          <SettingsPanel
            settings={settings}
            onChange={setSettings}
            onStart={handleStart}
            hasActiveGame={hasActiveGame}
            availableGroups={availableGroups}
            translate={t}
          />
        ) : (
          <section className="game-screen">
            <div className="game-screen__actions">
              <button type="button" className="ghost" onClick={handleReturnToMenu}>
                {t('game.returnToMenu')}
              </button>
              <button
                type="button"
                className="ghost"
                onClick={handleRestart}
                disabled={!hasActiveGame}
              >
                {t('controls.restart')}
              </button>
            </div>

            <StatsBar
              moves={game.moves}
              secondsElapsed={game.secondsElapsed}
              isComplete={game.isComplete}
              players={game.players}
              currentPlayerIndex={game.currentPlayerIndex}
              translate={t}
            />

            <GameBoard
              cards={game.cards}
              animalsById={localizedAnimalsById}
              onCardClick={handleCardClick}
              isInteractive={isInteractive}
              translate={t}
              gridSize={game.activeSettings?.gridSize ?? settings.gridSize}
            />

            <DeckPanel
              animals={localizedMatchedAnimals}
              currentIndex={deckIndex}
              onPrev={handlePrevDeck}
              onNext={handleNextDeck}
              translate={t}
            />

            <CompletionBanner
              visible={game.isComplete}
              moves={game.moves}
              secondsElapsed={game.secondsElapsed}
              players={game.players}
              translate={t}
              onRestart={handleRestart}
            />
          </section>
        )}
      </main>

      {modalAnimal && (
        <MatchedAnimalModal animal={modalAnimal} onClose={handleCloseModal} translate={t} />
      )}
      <InfoModal
        visible={isAboutOpen}
        title={t('info.about.title')}
        closeLabel={infoCloseLabel}
        onClose={() => setIsAboutOpen(false)}
      >
        {aboutParagraphs.map((paragraph, index) => (
          <p key={`about-paragraph-${index}`}>{paragraph}</p>
        ))}
      </InfoModal>
      <InfoModal
        visible={isHelpOpen}
        title={t('info.help.title')}
        closeLabel={infoCloseLabel}
        onClose={() => setIsHelpOpen(false)}
      >
        <p>{helpIntro}</p>
        <ol className="info-modal__steps">
          {helpSteps.map((step) => (
            <li key={step.title}>
              <span className="info-modal__step-title">{step.title}</span>
              <p>{step.description}</p>
            </li>
          ))}
        </ol>
        <div className="info-modal__tips">
          <span className="info-modal__tips-title">{helpTipsTitle}</span>
          <ul>
            {helpTips.map((tip, index) => (
              <li key={`help-tip-${index}`}>{tip}</li>
            ))}
          </ul>
        </div>
      </InfoModal>
      <FinalResultModal
        visible={showFinalResult}
        moves={game.moves}
        secondsElapsed={game.secondsElapsed}
        players={game.players}
        matchedAnimalsCount={game.matchedAnimals.length}
        translate={t}
        onClose={handleCloseFinalResult}
        onRestart={handleRestart}
      />
    </div>
  );
}
