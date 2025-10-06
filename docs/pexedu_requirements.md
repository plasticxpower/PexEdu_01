# PexEdu Build Requirements

This document is a single-source brief you can feed into another coding assistant to recreate the PexEdu application. It captures the product goals, data model, UI, and implementation rules observed in the existing project.

## 1. Product Vision
- Deliver a bilingual (English/Czech) wildlife-themed memory game inspired by classic pexeso.
- Players pick an animal group, choose a card grid (12/18/24 cards), and match pairs to fill a discovery deck.
- Support solo or pass-and-play multiplayer for up to four players, tracking per-player scores and time on the same device.
- Emphasize educational value: each animal reveals descriptive facts once matched.

## 2. Technology Stack & Tooling
- Frontend: React 18 with TypeScript, bundled by Vite 5 using `@vitejs/plugin-react`.
- State is managed with React hooks; no global state library.
- Internationalization: `i18next` with `react-i18next` and `i18next-browser-languagedetector`.
- Utility modules handle randomness, timing, and asset path resolution.
- Build commands:
  - `npm install`
  - `npm run dev` (Vite dev server)
  - `npm run build` (type-check with `tsc`, then Vite production build)
  - `npm run preview` (serve production build)
  - `npm run lint` (ESLint with React & hooks plugins)
- Configure deployment base path via `VITE_BASE_PATH` (mirrors `vite.config.ts`).

## 3. Domain Data & Types
- Primary dataset lives in `data/animals.json` as an array of entries:
  - `id`, `group` (`mammals` | `fish` | `amphibians` | `reptiles` | `birds`), `commonName`, `scientificName`, `size`, `lifeExpectancy`, `habitat`, `funFact`, `image`.
- Czech locale overrides in `data/animals.locale.cs.json` provide per-animal translations for selected fields.
- Core TypeScript types (`src/types.ts`):
  - `AnimalEntry` mirrors the dataset shape.
  - `GameSettings`: `{ group, gridSize (12|18|24), playerCount (1–4) }`.
  - `CardData`: memory card state (`id`, `animalId`, `revealed`, `matched`).
  - `AnimalGroup` union type for the allowed group names.
- Assets reside under `public/assets/`:
  - `animals/` (per-animal imagery),
  - `icons/` (group icons),
  - `flags/` (for the language switcher),
  - `graphics/Realistic_lion_standing_202510040825.mp4` (final celebration loop),
  - `placeholder.svg` fallback art.

## 4. High-Level App Structure
- Entry point (`src/main.tsx`) mounts `<App />` inside `React.StrictMode` and imports global CSS and i18n setup.
- `App.tsx` orchestrates data preparation, localization, view switching, and wires UI components to the game engine.
- `useGameEngine` hook encapsulates all gameplay state (cards, matches, players, timers).
- UI components under `src/components/` render settings, board, stats, deck, modals, and language switcher.
- Global styles live in `src/index.css`; utilities under `src/utils/`; i18n resources under `src/i18n/`.

## 5. Gameplay Flow
1. **Initial state**: show the settings screen with default `group=mammals`, `gridSize=12`, `playerCount=1`.
2. **Start game** (`startGame(settings)`):
   - Filter animals by selected group.
   - Sample `gridSize/2` unique animals; duplicate each to create card pairs; shuffle.
   - Initialize players array based on `playerCount`; reset moves, timers, matches.
   - Begin global timer that also increments the active player's personal time.
3. **During play**:
   - Clicking a card when interactive reveals it; at two reveals the engine locks input.
   - If both cards share `animalId`, mark them `matched`, increment current player's score, add the animal to the matched collection, and clear the selection after 300 ms (without switching turns).
   - On mismatch, schedule cards to flip back after 1 s and advance to the next player (cyclical order).
   - Timer pauses whenever a modal is open and resumes on close if the game is still running.
4. **Match reveal modal** (`MatchedAnimalModal`):
   - Pops up after each new match, showing the animal image and facts.
   - User can close via click, Escape, Enter, or Space; closing resumes the timer.
5. **Discovery deck** (`DeckPanel`):
   - Updates instantly after each successful match; navigable with previous/next arrows.
   - Displays image plus factual bullet list (size, lifespan, habitat, fun fact).
6. **Completion**:
   - When every card is marked matched, stop timer, mark game complete, and show `CompletionBanner` in-line.
   - After the user closes any open match modal, show `FinalResultModal` overlay with celebration video, aggregate stats, and per-player breakdown.
7. **Post-game actions**:
   - Restart button uses the last active settings (`restart()`).
   - Return to menu (`reset()`) clears engine state and shows the settings UI.

## 6. UI Composition & Styling Expectations
- **Layout**:
  - Root `.app` container is centered, max width 1200 px, vertical stack with generous spacing.
  - Background gradient from pale teal to cream; rounded cards with soft shadows.
  - Mobile-first CSS with responsive grid adjustments (CSS uses `data-grid-size` to size the board).
- **Header**:
  - Title + description on the left; `LanguageSwitcher` positioned top-right with flag icon and chevron.
  - Language menu opens as a floating listbox with active state highlight.
- **Settings Screen** (`SettingsPanel`):
  - Pills for animal groups rendered with icon, label, and gradient highlight when selected.
  - Grid size and player count options share pill styling.
  - Start button text switches between “Start the Adventure” (no active game) and “Apply settings” (mid-game); disabled if the selected group lacks enough animals for the chosen grid.
- **Game Screen**:
  - Action row with “Return to menu” and “Restart” ghost buttons.
  - `StatsBar`: move count, elapsed time (`mm:ss`), optional multi-player scoreboard with active-player highlight and `aria-live` updates.
  - `GameBoard`: responsive grid of `.memory-card` buttons; front shows animal photo + name, back shows group icon or “Flip to reveal”.
  - `DeckPanel`: shows discovery count, navigation arrows, image, scientific name, and fact list.
  - `CompletionBanner`: gradient card summarizing moves and total time, plus restart CTA.
- **Modals**:
  - `MatchedAnimalModal`: centered card with image, details in definition list, and “Keep playing” button.
  - `FinalResultModal`: full-screen overlay containing a looping but capped video (paused just before end to avoid black frames), summary stats, per-player list, and Restart/Continue buttons.
- **Styling utilities**:
  - `resolveAssetPath` ensures asset URLs respect `import.meta.env.BASE_URL` and handles external URLs; `PLACEHOLDER_IMAGE` is used whenever a path is missing.
  - CSS defines color variables (`--primary`, `--accent`, etc.) and shadows used across components.

## 7. Game Engine Responsibilities (`useGameEngine`)
- Maintains state refs for cards, matched animals, selected cards, players, timers, and lock status to prevent double interactions.
- Exposes API: `startGame`, `restart`, `revealCard`, `reset`, `pauseTimer`, `resumeTimer`, plus derived data (`isRunning`, `isComplete`, `moves`, `secondsElapsed`, `currentPlayerIndex`, etc.).
- Locks input while two cards are being evaluated; unlocks after timeout or immediate match processing.
- Uses `window.setInterval` for timers and cleans up intervals/timeouts on reset or component unmount.
- Adds matched animals to the discovery list only once even if their cards are revisited.

## 8. Internationalization
- Supported locales: `en` (default) and `cs`.
- `i18next-browser-languagedetector` checks query string, `localStorage`, then browser language; selections persist.
- `LanguageSwitcher` lets users toggle manually; current language icon and label reflect selection.
- Czech locale merges translation overrides for selected animal fields (`commonName`, `size`, etc.) using `LOCALE_OVERRIDES`.
- All user-visible strings flow through the translation layer (`translate` prop) with pluralization for labels such as pairs and players.

## 9. Accessibility & UX Notes
- Buttons use semantic `<button>` elements with descriptive `aria-label`s where needed (deck arrows, options).
- Stats and completion messages use `aria-live="polite"` to announce updates non-intrusively.
- Modals:
  - Use `role="dialog"` and `aria-modal="true"`.
  - Close on overlay click or keyboard shortcuts (Escape always; Enter/Space for the match modal).
  - Prevent timer from running while visible.
- Language menu behaves like a listbox (`aria-haspopup`, `aria-expanded`, `role="option"`).
- Ensure focus management respects these semantics when rebuilding (return focus to the invoking control after modal close).
- Provide hover/focus states consistent with the gradient theme; respect disabled states (opacity reduction, pointer disable).

## 10. Asset Handling & Media
- All relative asset requests should run through `resolveAssetPath` to honor the runtime base URL.
- When an asset path is missing, fall back to `PLACEHOLDER_IMAGE`.
- `FinalResultModal` embeds `assets/graphics/Realistic_lion_standing_202510040825.mp4`:
  - Autoplay, muted, `playsInline`.
  - Custom effect keeps playback near the loop point by pausing ~0.3 s before the natural end.
- Group icons expected under `public/assets/icons/{group}.png`.
- Flag icons for English and Czech under `public/assets/flags/{code}.svg`.

## 11. CSS & Visual Identity
- Global font: `Inter`, with system fallbacks.
- Palette defined on `:root`; notable colors:
  - Text: `--ink` (#3a322a) with muted variations.
  - Surfaces: `--surface`, `--surface-muted`, `--surface-alt`.
  - Accent gradients: `--primary` (#4a7c8a), `--accent` (#c7944a).
- Gradients and shadows provide a polished, warm aesthetic; cards and panels have rounded corners (16–28 px).
- The board is responsive; CSS uses `aspect-ratio` and `grid-template-columns` keyed by `data-grid-size`.
- Start button has two visual states (baseline and “active” with brighter gradient) depending on whether a game is already running.

## 12. Directory Expectations
```
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── index.css
│   ├── types.ts
│   ├── hooks/useGameEngine.ts
│   ├── components/
│   │   ├── SettingsPanel.tsx
│   │   ├── GameBoard.tsx
│   │   ├── DeckPanel.tsx
│   │   ├── StatsBar.tsx
│   │   ├── CompletionBanner.tsx
│   │   ├── MatchedAnimalModal.tsx
│   │   ├── FinalResultModal.tsx
│   │   └── LanguageSwitcher.tsx
│   ├── utils/
│   │   ├── assets.ts
│   │   ├── random.ts
│   │   └── time.ts
│   └── i18n/
│       ├── index.ts
│       ├── en.json
│       └── cs.json
├── data/
│   ├── animals.json
│   ├── animals.locale.cs.json
│   └── animals_source.json
├── public/assets/...
├── scripts/data_pipeline.py
├── package.json
└── vite.config.ts
```

## 13. Data Pipeline (Optional Enhancement)
- Python script `scripts/data_pipeline.py` crawls Encyclopædia Britannica for each seed animal (`data/animals_source.json`), extracts descriptive text (size, lifespan, habitat, fun fact), downloads lead imagery, and writes `data/animals.json`.
- Supports resumable runs, refresh flags, and image filtering to avoid illustrations.
- Requires `requests` and `beautifulsoup4`; respects cache folders under `public/assets/animals`.

## 14. Non-Functional Requirements
- Responsive layout should remain usable on mobile (single-column stacking) through desktop (grid layout with board, stats, and deck side by side).
- Keep gameplay smooth: avoid unnecessary re-renders (use memoization for derived maps and arrays).
- Ensure timers clear on unmount to prevent leaks.
- Provide lazy loading for images (`loading="lazy"` already used) and small asset payloads for quick startup.

Use this document as the canonical reference when reconstructing the PexEdu application.
