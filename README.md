# PexEdu

PexEdu is a bilingual (English/Czech) wildlife-themed pexeso/memory game delivered as a mobile-first React application. Players pick an animal group, choose a card grid (12, 18, or 24 cards), flip pairs to find matches, and review their collected animals in a dedicated discovery deck.

## Getting Started

### Prerequisites

- Node.js 18+
- npm (or a compatible package manager)
- Python 3.9+ with pip

### Install dependencies

npm install

### Run the development server

npm run dev

The app is configured with Vite and will be ready for GitHub Pages deployment (vite.config.ts honours VITE_BASE_PATH).

### Linting

npm run lint

## Data pipeline

Animal metadata and images are sourced from Britannica using the single script scripts/data_pipeline.py.

1. Ensure Python dependencies are available: pip install requests beautifulsoup4
2. (Optional) Inspect or edit the seed list in data/animals_source.json (requires group, commonName, scientificName).
3. Run the pipeline (network access required): python scripts/data_pipeline.py
   - Images are saved under public/assets/animals/.
   - The compiled dataset is written to data/animals.json.
   - Use --limit N while testing or --skip-images to collect text only.

Note: In this workspace network access is restricted, so data/animals.json currently contains placeholder image paths (/assets/placeholder.svg). When you run the script in an environment with outbound access, the dataset and image assets will be refreshed automatically.

## Internationalisation

Translations live in src/i18n/en.json and src/i18n/cs.json. i18next with automatic language detection (query string, localStorage, navigator) is configured in src/i18n/index.ts. The language switcher component offers manual toggling.

## Project Structure

- src/ – React application (components, hooks, utilities, types, i18n)
- data/ – Source seed list and generated dataset for animals
- public/assets/ – Static assets, including downloaded animal imagery
- scripts/data_pipeline.py – Single data collection script (Britannica)

## Deployment

The project is Vite-based; npm run build emits production assets under dist/. Configure VITE_BASE_PATH to match your GitHub Pages repository path before building if the site will be hosted in a subdirectory.
