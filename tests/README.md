# Tests

Automated tests live with the backend:

- `backend/tests/test_api.py` — API contract (states, districts, simulate, risk analyze, infrastructure, AI endpoints, validation → 422, health/providers)
- `backend/tests/test_risk_engine.py` — risk-engine determinism, weights, bands, zone generation

Run them:

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests -q     # Windows
pytest tests -q                                  # macOS / Linux
```

Expected: **24 passed**.

Frontend quality gates (no unit-test framework in this MVP):

```bash
cd frontend
npm run lint
npm run build
```

End-to-end smoke check: start backend (`uvicorn app.main:app --reload`) and frontend (`npm run dev`), then open <http://localhost:3000> and click **Load Demo Scenario** → **Run Simulation**.
