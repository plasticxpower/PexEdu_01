import { useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import animalsJson from '../data/animals.json';
import csLocaleOverrides from '../data/animals.locale.cs.json';
import { CompletionBanner } from './components/CompletionBanner';
import { DeckPanel } from './components/DeckPanel';
import { GameBoard } from './components/GameBoard';
import { LanguageSwitcher } from './components/LanguageSwitcher';
import { MatchedAnimalModal } from './components/MatchedAnimalModal';
import { SettingsPanel } from './components/SettingsPanel';
import { StatsBar } from './components/StatsBar';
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
  return {
    ...animal,
    ...overrides,
  };
}

export default function App() {
  const { t, i18n } = useTranslation();
  const animals = useMemo(() => animalsJson as AnimalEntry[], []);
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

  const handleStart = () => {
    game.startGame(settings);
    setModalAnimalId(null);
    setView('game');
  };

  const handleRestart = () => {
    setModalAnimalId(null);
    game.restart();
  };

  const handleReturnToMenu = () => {
    game.reset();
    setDeckIndex(0);
    previousMatchCount.current = 0;
    setModalAnimalId(null);
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
  };

  const hasActiveGame = game.activeSettings !== null;
  const isInteractive = game.isRunning && !game.isComplete && !modalAnimalId;

  const localizedMatchedAnimals = useMemo(() => {
    return game.matchedAnimals.map((animal) => localizedAnimalsById[animal.id] ?? animal);
  }, [game.matchedAnimals, localizedAnimalsById]);

  const modalAnimal = modalAnimalId
    ? localizedAnimalsById[modalAnimalId] ?? animalsById[modalAnimalId]
    : null;

  return (
    <div className="app">
      <header className="app__header">
        <div>
          <h1>{t('app.title')}</h1>
          <p>{t('app.description')}</p>
        </div>
        <LanguageSwitcher />
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
    </div>
  );
}
