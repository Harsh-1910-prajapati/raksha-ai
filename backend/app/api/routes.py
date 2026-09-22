"""RakshaAI API routes."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from app.config import get_settings
from app.gemini import get_gemini_provider
from app.gemini.client import GeminiClientError
from app.gemini.provider import build_context
from app.infrastructure.providers import get_infrastructure_provider
from app.risk_engine.engine import run_scenario
from app.schemas.scenario import ScenarioInput
from app.services import locations
from app.services.geo_data import get_geo_provider

router = APIRouter()


def _with_ai_provider(force_mock: bool = False):
    return get_gemini_provider(force_mock=force_mock)


def _simulation_body(raw: dict[str, Any]) -> dict[str, Any]:
    sim = raw.get("simulation")
    if not isinstance(sim, dict) or "risk" not in sim:
        raise HTTPException(
            status_code=422,
            detail="Body must contain a valid 'simulation' object produced by POST /api/scenarios/simulate.",
        )
    return sim


# --------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@router.get("/health")
def health() -> dict[str, Any]:
    geo = get_geo_provider()
    infra = get_infrastructure_provider()
    ai = _with_ai_provider()
    return {
        "status": "ok",
        "service": "RakshaAI API",
        "time": datetime.now(timezone.utc).isoformat(),
        "providers": {
            "geo": geo.status(),
            "infrastructure": infra.status(),
            "ai": {"provider": ai.name, "available": True},
        },
        "gemini": {
            "configured": get_gemini_provider().name == "gemini",
            "note": "Set GEMINI_API_KEY to enable live Gemini reasoning.",
        },
        "earthEngine": geo.status(),
        "maps": {
            "frontendKeyConfigured": bool(get_settings().google_maps_api_key),
            "fallback": "Frontend uses a built-in SVG risk map when no key is set.",
        },
    }


# --------------------------------------------------------------------------
# Locations
# ---------------------------------------------------------------------------


@router.get("/api/locations/states")
def list_states() -> dict[str, Any]:
    return {
        "states": locations.get_states(),
        "sourceLabel": "RakshaAI demo location catalogue (India)",
    }


@router.get("/api/locations/{state}/districts")
def list_districts(state: str) -> dict[str, Any]:
    if not locations.state_exists(state):
        raise HTTPException(status_code=404, detail=f"State '{state}' not found in catalogue")
    return {
        "state": state,
        "districts": locations.get_districts(state),
        "sourceLabel": "RakshaAI demo location catalogue (India)",
    }


@router.get("/api/locations/disaster-types")
def list_disaster_types() -> dict[str, Any]:
    return locations.get_disaster_types()


# --------------------------------------------------------------------------
# Scenario + risk
# ---------------------------------------------------------------------------


@router.post("/api/scenarios/simulate")
def simulate_scenario(input: ScenarioInput) -> dict[str, Any]:
    try:
        return run_scenario(input)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/api/risk/analyze")
def analyze_risk(input: ScenarioInput) -> dict[str, Any]:
    try:
        result = run_scenario(input)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "disasterType": result["disasterType"],
        "state": result["state"],
        "district": result["district"],
        "overall": result["risk"]["overall"],
        "components": result["risk"]["components"],
        "exposure": result["exposure"],
        "zones": result["zones"],
        "inferenceNote": result["risk"]["inferenceNote"],
    }


# --------------------------------------------------------------------------
# Infrastructure
# ---------------------------------------------------------------------------


@router.get("/api/infrastructure")
def infrastructure(
    state: str = Query(..., min_length=2),
    district: str = Query(..., min_length=2),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius: float = Query(80.0, gt=0),
    windSpeed: float = Query(0.0, ge=0),
    rainfall: float = Query(0.0, ge=0),
    stormSurge: float = Query(0.0, ge=0),
) -> dict[str, Any]:
    provider = get_infrastructure_provider()
    try:
        data = provider.list_for(
            state,
            district,
            latitude,
            longitude,
            radius,
            {"windSpeed": windSpeed, "rainfall": rainfall, "stormSurge": stormSurge, "impactRadius": radius},
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return data.model_dump(mode="json")


# --------------------------------------------------------------------------
# AI endpoints
# ---------------------------------------------------------------------------


@router.post("/api/ai/analyze")
def ai_analyze(
    body: dict[str, Any] = Body(...),
    force_mock: bool = Query(False),
) -> dict[str, Any]:
    sim = _simulation_body(body)
    context = build_context(sim)
    provider = _with_ai_provider(force_mock)
    try:
        data = provider.analyze(context)
        data["ai_provider"] = provider.name or "gemini"
    except GeminiClientError as exc:
        data = get_gemini_provider(force_mock=True).analyze(context)
        data["provider_note"] = f"Live Gemini failed ({exc}); switched to deterministic fallback."
        data["ai_provider"] = "mock"
    return data


@router.post("/api/ai/action-plan")
def ai_action_plan(
    body: dict[str, Any] = Body(...),
    force_mock: bool = Query(False),
) -> dict[str, Any]:
    sim = _simulation_body(body)
    context = build_context(sim)
    provider = _with_ai_provider(force_mock)
    try:
        data = provider.action_plan(context)
        data["ai_provider"] = provider.name or "gemini"
    except GeminiClientError as exc:
        data = get_gemini_provider(force_mock=True).action_plan(context)
        data["provider_note"] = f"Live Gemini failed ({exc}); switched to deterministic fallback."
        data["ai_provider"] = "mock"
    return data


@router.post("/api/ai/alert")
def ai_alert(
    body: dict[str, Any] = Body(...),
    force_mock: bool = Query(False),
) -> dict[str, Any]:
    sim = _simulation_body(body)
    alert_type = body.get("alertType", "citizen")
    if alert_type not in {"citizen", "authority"}:
        alert_type = "citizen"
    context = build_context(sim)
    provider = _with_ai_provider(force_mock)
    try:
        data = provider.alert(context, alert_type)
        data["ai_provider"] = provider.name or "gemini"
    except GeminiClientError as exc:
        data = get_gemini_provider(force_mock=True).alert(context, alert_type)
        data["provider_note"] = f"Live Gemini failed ({exc}); switched to deterministic fallback."
        data["ai_provider"] = "mock"
    data["alert_type"] = alert_type
    return data


@router.post("/api/ai/state-brief")
def ai_state_brief(
    body: dict[str, Any] = Body(...),
    force_mock: bool = Query(False),
) -> dict[str, Any]:
    sim = _simulation_body(body)
    context = build_context(sim)
    provider = _with_ai_provider(force_mock)
    try:
        data = provider.state_brief(context)
        data["ai_provider"] = provider.name or "gemini"
    except GeminiClientError as exc:
        data = get_gemini_provider(force_mock=True).state_brief(context)
        data["provider_note"] = f"Live Gemini failed ({exc}); switched to deterministic fallback."
        data["ai_provider"] = "mock"
    data["state"] = context["state"]
    data["generatedAt"] = datetime.now(timezone.utc).isoformat()
    return data