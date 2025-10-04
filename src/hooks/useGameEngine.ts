import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

import type { AnimalEntry, GameSettings } from '../types';
import { sample, shuffle } from '../utils/random';

interface UseGameEngineArgs {
  animals: AnimalEntry[];
}

interface PlayerState {
  id: number;
  score: number;
}

interface UseGameEngineResult {
  cards: Array<{
    id: string;
    animalId: string;
    revealed: boolean;
    matched: boolean;
  }>;
  activeSettings: GameSettings | null;
  matchedAnimals: AnimalEntry[];
  players: PlayerState[];
  currentPlayerIndex: number;
  moves: number;
  secondsElapsed: number;
  isRunning: boolean;
  isComplete: boolean;
  startGame: (settings: GameSettings) => void;
  restart: () => void;
  revealCard: (cardId: string) => void;
  reset: () => void;
  pauseTimer: () => void;
  resumeTimer: () => void;
}

export function useGameEngine({ animals }: UseGameEngineArgs): UseGameEngineResult {
  const [cards, setCards] = useState<UseGameEngineResult['cards']>([]);
  const cardsRef = useRef(cards);
  const [activeSettings, setActiveSettings] = useState<GameSettings | null>(null);
  const [matchedAnimals, setMatchedAnimals] = useState<AnimalEntry[]>([]);
  const [players, setPlayers] = useState<PlayerState[]>([{ id: 0, score: 0 }]);
  const [currentPlayerIndex, setCurrentPlayerIndex] = useState(0);
  const [moves, setMoves] = useState(0);
  const [secondsElapsed, setSecondsElapsed] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [isComplete, setIsComplete] = useState(false);
  const [selectedCardIds, setSelectedCardIds] = useState<string[]>([]);
  const timerRef = useRef<number | null>(null);
  const hideTimeoutRef = useRef<number | null>(null);
  const lockRef = useRef(false);
  const totalPlayers = players.length;

  useEffect(() => {
    cardsRef.current = cards;
  }, [cards]);


  const animalsById = useMemo(() => {
    return animals.reduce<Record<string, AnimalEntry>>((acc, animal) => {
      acc[animal.id] = animal;
      return acc;
    }, {});
  }, [animals]);

  const startTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
    }
    timerRef.current = window.setInterval(() => {
      setSecondsElapsed((value) => value + 1);
    }, 1000);
  }, []);

  const stopTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const pauseTimer = useCallback(() => {
    if (timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
  }, []);

  const resumeTimer = useCallback(() => {
    if (isRunning && !isComplete && timerRef.current === null) {
      timerRef.current = window.setInterval(() => {
        setSecondsElapsed((value) => value + 1);
      }, 1000);
    }
  }, [isRunning, isComplete]);

  const resetTimers = useCallback(() => {
    stopTimer();
    if (hideTimeoutRef.current !== null) {
      window.clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
  }, [stopTimer]);

  const reset = useCallback(() => {
    resetTimers();
    const singlePlayer = [{ id: 0, score: 0 }];
    setCards([]);
    setActiveSettings(null);
    setMatchedAnimals([]);
    setPlayers(singlePlayer);
    setCurrentPlayerIndex(0);
    setMoves(0);
    setSecondsElapsed(0);
    setIsRunning(false);
    setIsComplete(false);
    setSelectedCardIds([]);
    lockRef.current = false;
  }, [resetTimers]);

  const createCards = useCallback((pickedAnimals: AnimalEntry[]) => {
    const duplicated = pickedAnimals.flatMap((animal) => [
      {
        id: animal.id + '-a',
        animalId: animal.id,
        revealed: false,
        matched: false,
      },
      {
        id: animal.id + '-b',
        animalId: animal.id,
        revealed: false,
        matched: false,
      },
    ]);
    return shuffle(duplicated);
  }, []);

  const startGame = useCallback(
    (settings: GameSettings) => {
      const groupAnimals = animals.filter((item) => item.group === settings.group);
      if (groupAnimals.length < settings.gridSize / 2) {
        throw new Error('Not enough animals available for requested grid size');
      }
      resetTimers();
      const playerCount = settings.playerCount ?? 1;
      const initialPlayers = Array.from({ length: playerCount }, (_, index) => ({ id: index, score: 0 }));
      setPlayers(initialPlayers);
      setCurrentPlayerIndex(0);
      const picked = sample(groupAnimals, settings.gridSize / 2);
      setCards(createCards(picked));
      setActiveSettings(settings);
      setMatchedAnimals([]);
      setMoves(0);
      setSecondsElapsed(0);
      setIsRunning(true);
      setIsComplete(false);
      setSelectedCardIds([]);
      lockRef.current = false;
      startTimer();
    },
    [animals, createCards, resetTimers, startTimer]
  );

  const restart = useCallback(() => {
    if (activeSettings) {
      startGame(activeSettings);
    }
  }, [activeSettings, startGame]);

  const markCardsAs = useCallback((cardIds: string[], changes: Partial<UseGameEngineResult['cards'][number]>) => {
    setCards((prev) =>
      prev.map((card) => (cardIds.includes(card.id) ? { ...card, ...changes } : card))
    );
  }, []);

  const advancePlayer = useCallback(() => {
    if (totalPlayers <= 1) {
      return;
    }
    setCurrentPlayerIndex((index) => (index + 1) % totalPlayers);
  }, [totalPlayers]);

  const revealCard = useCallback(
    (cardId: string) => {
      if (!isRunning || lockRef.current) {
        return;
      }
      const card = cardsRef.current.find((item) => item.id === cardId);
      if (!card || card.revealed || card.matched) {
        return;
      }
      markCardsAs([cardId], { revealed: true });
      setSelectedCardIds((current) => {
        if (current.includes(cardId)) {
          return current;
        }
        const next = [...current, cardId];
        if (next.length === 2) {
          lockRef.current = true;
          setMoves((value) => value + 1);
          const [firstId, secondId] = next;
          const firstCard = cardsRef.current.find((item) => item.id === firstId);
          const secondCard = cardsRef.current.find((item) => item.id === secondId);
          if (firstCard && secondCard) {
            if (firstCard.animalId === secondCard.animalId) {
              markCardsAs([firstId, secondId], { matched: true });
              setPlayers((prev) =>
                prev.map((player, index) =>
                  index === currentPlayerIndex ? { ...player, score: player.score + 1 } : player
                )
              );
              const matchedAnimal = animalsById[firstCard.animalId];
              setMatchedAnimals((prev) => {
                if (prev.some((entry) => entry.id === matchedAnimal.id)) {
                  return prev;
                }
                return [...prev, matchedAnimal];
              });
              window.setTimeout(() => {
                lockRef.current = false;
                setSelectedCardIds([]);
              }, 300);
            } else {
              advancePlayer();
              if (hideTimeoutRef.current !== null) {
                window.clearTimeout(hideTimeoutRef.current);
              }
              hideTimeoutRef.current = window.setTimeout(() => {
                markCardsAs([firstId, secondId], { revealed: false });
                lockRef.current = false;
                setSelectedCardIds([]);
                hideTimeoutRef.current = null;
              }, 800);
            }
          }
        }
        return next;
      });
    },
    [animalsById, isRunning, markCardsAs, currentPlayerIndex, advancePlayer]
  );

  useEffect(() => {
    if (cards.length > 0 && cards.every((card) => card.matched)) {
      setIsComplete(true);
      setIsRunning(false);
      stopTimer();
    }
  }, [cards, stopTimer]);

  useEffect(() => () => reset(), [reset]);

  return {
    cards,
    activeSettings,
    matchedAnimals,
    players,
    currentPlayerIndex,
    moves,
    secondsElapsed,
    isRunning,
    isComplete,
    startGame,
    restart,
    revealCard,
    reset,
    pauseTimer,
    resumeTimer,
  };
}
