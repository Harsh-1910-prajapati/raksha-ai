# RakshaAI — Pre-Deployment Review Report

Date: 2026-09-22 · Scope: final pre-submission review for **Build with AI: Code for Communities — Second Edition**.

## Verdict

**Deployment-ready** after the fixes below. Backend tests 24/24, frontend lint + production build clean, no secrets in the repo.

## Issues found in review (A–J) and fixes applied

| # | Issue | Fix |
|---|---|---|
| A | `gcloud builds submit` uses the repo-root context, but the Dockerfile lived under `backend/` → build would fail. Root context would also ship `.git/.env/node_modules` (no root `.dockerignore`). | Moved to root `Dockerfile`; added root `.dockerignore` (ignores git, env, node_modules, tests, docs). Deleted `backend/Dockerfile` + `backend/.dockerignore`. |
| B | Docker CMD hardcoded port 8080; Cloud Run injects `$PORT`. | `CMD sh -c "uvicorn ... --port ${PORT:-8080}"`; HEALTHCHECK also honours `$PORT`. |
| C | CORS default only allowed one Vercel origin (dash-prefixed preview URLs would be blocked). | `config.py` now compiles wildcard origins (`https://*.vercel.app`) into `cors_origin_regex`, keeps exact origins in `allow_origins`; `main.py` passes both. Defaults updated in `.env.example` (×2). Verified: exact + wildcard match, evil.com rejected. |
| D | README deploy section: `--set-env-vars CORS_ORIGINS=...` comma gotcha + insecure key guidance. | Documented `^,` gcloud escaping, quoted flag, and `--set-secrets=GEMINI_API_KEY=gemini-api-key:latest` with a `gcloud secrets create` snippet. |
| E | `frontend/README.md` was stale create-next-app boilerplate (wrong path `app/page.tsx`). | Rewrote: real stack, run steps, env table, scripts, `src/` structure, demo-mode note. |
| F | Missing `docs/SETUP.md`, `docs/FINAL_REPORT.md`; empty root `tests/`. | Added all three (full local setup, this report, tests pointer). |
| G | `next-env.d.ts` was ignored but is auto-generated tooling that should be committed. | Removed from `.gitignore` (file now tracked). |
| H | `/health` said "offline canvas map" but fallback is SVG. | Corrected wording to "built-in SVG risk map". |
| I | `/api/risk/analyze` could 500 on invalid input (no `ValueError` wrapper, unlike `/simulate`). | Added `ValueError → 422` handling. |
| J | Frontend unreachable-backend error was dev-only, unhelpful beyond localhost. | Error now includes the resolved backend URL and a `NEXT_PUBLIC_API_URL` hint. |

## What was verified

- **Backend:** `pytest tests -q` → **24 passed** (risk-engine determinism/weights/bands, API contract incl. 422 validation, AI fallback to mock).
- **Frontend:** `npm run lint` clean; `npm run build` clean (static `/` + `/_not-found`, TypeScript pass).
- **CORS:** regex compile + match test (exact origins and wildcard subdomains allowed; non-Vercel origin rejected).
- **Secrets:** grep for `AIza…`, `sk-…`, private keys → **no matches**; git status shows no `.env` files tracked.
- **Demo/fallback honesty:** DEMO DATA badges, header provider status, mock AI labelling, SVG-map fallback, Gemini failure → deterministic fallback with `provider_note` — confirmed present.
- **Responsive UI:** grid/flex wrap at all breakpoints; printable State Emergency Brief with print CSS.

## Remaining verification before/as-part-of submission

- Live Gemini/Maps/Earth Engine/Firebase cannot be tested here (no keys) — fallbacks cover this; verify with real keys in Cloud Run/Vercel.
- `git init` exists but **zero commits** — commit intentionally before pushing (per your instruction this was left untouched).

## Deployment checklist (commands)

```bash
# repo root — push (after committing)
git add -A && git commit -m "..." && git push

# backend → Cloud Run
gcloud builds submit --tag gcr.io/YOUR_PROJECT/raksha-ai-backend .
echo -n "KEY" | gcloud secrets create gemini-api-key --data-file=-
gcloud run deploy raksha-ai-backend --image gcr.io/YOUR_PROJECT/raksha-ai-backend \
  --platform managed --region asia-south1 --allow-unauthenticated --port 8080 \
  --set-env-vars="CORS_ORIGINS=https://YOUR_FRONTEND.vercel.app,http://localhost:3000" \
  --set-secrets=GEMINI_API_KEY=gemini-api-key:latest

# frontend → Vercel
cd frontend && vercel           # set NEXT_PUBLIC_API_URL=https://<backend>-NEW-UID.a.run.app
```

## Production environment variables

- Backend (Cloud Run): `GEMINI_API_KEY` (Secret Manager), `GEMINI_MODEL` (optional), `CORS_ORIGINS`, `ENVIRONMENT=production`, `EARTH_ENGINE_*`/`FIREBASE_PROJECT_ID` (optional). `RISK_*_WEIGHT` defaults fine.
- Frontend (Vercel): `NEXT_PUBLIC_API_URL` (required, public), `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` (optional, public — lock by HTTP referrer).