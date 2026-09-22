"""API tests using FastAPI TestClient (no external services)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

VALID_SCENARIO = {
    "disasterType": "CYCLONE",
    "state": "Andhra Pradesh",
    "district": "Visakhapatnam",
    "latitude": 17.6868,
    "longitude": 83.2185,
    "windSpeed": 140,
    "rainfall": 220,
    "stormSurge": 2.5,
    "impactRadius": 80,
}


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "providers" in body


def test_locations_states():
    resp = client.get("/api/locations/states")
    assert resp.status_code == 200
    names = [s["name"] for s in resp.json()["states"]]
    assert "Andhra Pradesh" in names


def test_locations_districts():
    resp = client.get("/api/locations/Andhra%20Pradesh/districts")
    assert resp.status_code == 200
    names = [d["name"] for d in resp.json()["districts"]]
    assert "Visakhapatnam" in names


def test_locations_bad_state():
    resp = client.get("/api/locations/Nowhere/districts")
    assert resp.status_code == 404


def test_locations_disaster_types():
    resp = client.get("/api/locations/disaster-types")
    assert resp.status_code == 200
    ids = [d["id"] for d in resp.json()["disasterTypes"]]
    assert "CYCLONE" in ids and "FLOOD" in ids


def test_simulate_scenario():
    resp = client.post("/api/scenarios/simulate", json=VALID_SCENARIO)
    assert resp.status_code == 200
    body = resp.json()
    assert body["risk"]["overall"]["score"] > 0
    assert body["risk"]["overall"]["level"] in {"LOW", "MODERATE", "HIGH", "CRITICAL"}
    assert body["scenario"]["district"] == "Visakhapatnam"
    assert len(body["infrastructure"]["items"]) > 0


def test_simulate_invalid():
    bad = dict(VALID_SCENARIO, latitude=999)
    resp = client.post("/api/scenarios/simulate", json=bad)
    assert resp.status_code == 422


def test_risk_analyze():
    resp = client.post("/api/risk/analyze", json=VALID_SCENARIO)
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["components"].keys()) == {"flood", "wind", "population", "infrastructure", "accessibility"}


def test_infrastructure_demo():
    resp = client.get(
        "/api/infrastructure",
        params={
            "state": "Andhra Pradesh",
            "district": "Visakhapatnam",
            "latitude": 17.6868,
            "longitude": 83.2185,
            "radius": 80,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["counts"]["hospital"] >= 1


def test_ai_analyze_fallback():
    sim = client.post("/api/scenarios/simulate", json=VALID_SCENARIO).json()
    resp = client.post("/api/ai/analyze", json={"simulation": sim}, params={"force_mock": "true"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["ai_provider"] == "mock"
    assert body["summary"]


def test_ai_action_plan_fallback():
    sim = client.post("/api/scenarios/simulate", json=VALID_SCENARIO).json()
    resp = client.post("/api/ai/action-plan", json={"simulation": sim}, params={"force_mock": "true"})
    assert resp.status_code == 200
    assert resp.json()["immediateActions"]


def test_ai_alert_fallback():
    sim = client.post("/api/scenarios/simulate", json=VALID_SCENARIO).json()
    resp = client.post("/api/ai/alert", json={"simulation": sim, "alertType": "citizen"}, params={"force_mock": "true"})
    assert resp.status_code == 200
    body = resp.json()
    langs = [l["language"] for l in body["languages"]]
    assert langs == ["en", "hi", "te"]


def test_ai_state_brief_fallback():
    sim = client.post("/api/scenarios/simulate", json=VALID_SCENARIO).json()
    resp = client.post("/api/ai/state-brief", json={"simulation": sim}, params={"force_mock": "true"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["state"] == "Andhra Pradesh"


def test_ai_bad_body():
    resp = client.post("/api/ai/analyze", json={"foo": "bar"})
    assert resp.status_code == 422