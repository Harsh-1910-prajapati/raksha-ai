# RakshaAI — Setup Guide

Step-by-step local setup. The full product runs with **no API keys** (demo mode); add keys to enable live services.

## Prerequisites

- Python 3.11+ (developed on 3.13)
- Node.js 18+ (developed on 24)
- Optional: Google Cloud account (Cloud Run, Secret Manager), Vercel account

## 1. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env          # add GEMINI_API_KEY for live AI (optional)
uvicorn app.main:app --reload
```

Verify:

- Health: <http://localhost:8000/health>
- Swagger: <http://localhost:8000/docs>

The backend reads `backend/.env`. Data catalogue lives in repo-root `data/` (override with `RAKSHA_DATA_DIR`).

## 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local    # set NEXT_PUBLIC_API_URL if needed
npm run dev
```

Open <http://localhost:3000>. Default API URL is `http://localhost:8000`.

## 3. Environment Variables

Templates: root `.env.example`, `backend/.env.example`, `frontend/.env.example`.

| Variable | Where | Purpose | Required |
|---|---|---|---|
| `GEMINI_API_KEY` | backend | Live Gemini reasoning | No (mock fallback) |
| `GEMINI_MODEL` | backend | Model name | No (`gemini-2.0-flash`) |
| `CORS_ORIGINS` | backend | Allowed origins; `https://*.vercel.app` wildcards OK | No (sensible defaults) |
| `NEXT_PUBLIC_API_URL` | frontend | Backend base URL | No (`http://localhost:8000`) |
| `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | frontend | Live Maps | No (SVG fallback) |
| `EARTH_ENGINE_*` | backend | Earth Engine | No (demo provider) |
| `FIREBASE_PROJECT_ID` | backend | Firebase repo | No |
| `RISK_*_WEIGHT` | backend | Risk weights | No (defaults) |

Never commit real `.env` files — `.env*` is git-ignored (except `*.env.example`).

## 4. Tests

```bash
# backend (24 tests)
cd backend
.venv\Scripts\python.exe -m pytest tests -q     # Windows
pytest tests -q                                  # macOS/Linux

# frontend
cd frontend
npm run lint
npm run build
```

## 5. Deployment

See the **Deployment** section of the [root README](../README.md):

- Frontend → Vercel (`NEXT_PUBLIC_API_URL` in project settings)
- Backend → Cloud Run (root `Dockerfile`, `$PORT`-aware, secrets via Secret Manager `--set-secrets`)

## Troubleshooting

- **"Cannot reach the RakshaAI backend…"** — start the backend, or fix `NEXT_PUBLIC_API_URL`.
- **CORS errors in production** — add your frontend origin to `CORS_ORIGINS` (wildcards like `https://*.vercel.app` are supported).
- **Maps not showing** — expected without `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY`; the built-in SVG risk map is the fallback.
- **AI shows "mock"** — expected without `GEMINI_API_KEY`, or live call failed (response carries `provider_note`).
