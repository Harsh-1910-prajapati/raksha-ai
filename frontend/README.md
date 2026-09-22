# RakshaAI — Frontend

Next.js 16 + TypeScript + Tailwind CSS UI for RakshaAI: scenario form, risk map, infrastructure exposure, Gemini analysis, action plan, multilingual alerts and the printable State Emergency Brief.

## Run

```bash
npm install
cp .env.example .env.local   # optional
npm run dev                  # http://localhost:3000
```

## Environment (`.env.local`)

| Variable | Purpose | Default |
|---|---|---|
| `NEXT_PUBLIC_API_URL` | Backend base URL | `http://localhost:8000` |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | Live Google Maps overlay | empty → built-in SVG map |

Never commit `.env.local`. Keys are public client-side (`NEXT_PUBLIC_*`) — restrict Maps keys by HTTP referrer.

## Scripts

```bash
npm run dev      # development server
npm run build    # production build
npm run start    # serve the production build
npm run lint     # ESLint
```

## Structure

```text
src/
  app/            App Router pages (page.tsx = dashboard)
  components/     Header, ScenarioForm, RiskMap, AIAnalysisPanel, StateBriefPanel, …
  lib/            api.ts (REST client), types.ts, demo data helpers
```

The API client (`src/lib/api.ts`) surfaces descriptive errors in the UI (including unreachable-backend hints) instead of crashing.

## Demo Mode

With no backend or keys the UI runs on labelled demo data — look for **DEMO DATA** badges, the header provider status, and the disclaimer panel.

See the [root README](../README.md) for architecture, API reference and deployment.
