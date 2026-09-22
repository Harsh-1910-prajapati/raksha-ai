"""Risk-engine unit tests (deterministic, no external services)."""

from __future__ import annotations

import pytest
from app.risk_engine.accessibility import accessibility_risk
from app.risk_engine.elevation import elevation_risk
from app.risk_engine.flood import flood_risk
from app.risk_engine.overall import overall_risk
from app.risk_engine.risk_level import classify
from app.risk_engine.wind import wind_risk
from app.schemas.scenario import ScenarioInput
from pydantic import ValidationError


def test_classify_bands():
    assert classify(0) == "LOW"
    assert classify(25) == "LOW"
    assert classify(26) == "MODERATE"
    assert classify(50) == "MODERATE"
    assert classify(51) == "HIGH"
    assert classify(75) == "HIGH"
    assert classify(76) == "CRITICAL"
    assert classify(100) == "CRITICAL"


def test_flood_low():
    score, factors = flood_risk(rainfall_mm=10, storm_surge_m=0, elevation_m=200, coastal_proxy=0.1, flood_prone="low")
    assert 0 <= score <= 35
    assert isinstance(factors, list)


def test_flood_high():
    score, factors = flood_risk(rainfall_mm=320, storm_surge_m=3.0, elevation_m=2, coastal_proxy=0.9, flood_prone="critical")
    assert score >= 70
    assert any("rainfall" in f.lower() for f in factors)


def test_wind_zero():
    score, _ = wind_risk(0, 0)
    assert score == 0.0


def test_wind_high():
    score, factors = wind_risk(180, 0.8)
    assert score >= 70
    assert any("cyclonic" in f.lower() for f in factors)


def test_elevation():
    low_score, _ = elevation_risk(2, 0.9)
    high_elev_score, _ = elevation_risk(500, 0.0)
    assert low_score > high_elev_score


def test_accessibility():
    roads = [{"riskScore": 90, "type": "road"} for _ in range(4)]
    score, factors = accessibility_risk(roads, 10, 3000)
    assert 0 <= score <= 100


def test_overall_risk_weighting():
    components = {"flood": 80, "wind": 60, "population": 50, "infrastructure": 40, "accessibility": 30}
    total = overall_risk(components)
    expected = 80 * 0.30 + 60 * 0.25 + 50 * 0.20 + 40 * 0.15 + 30 * 0.10
    assert total == round(expected, 1)


def test_scenario_validation_invalid():
    with pytest.raises(ValidationError):
        ScenarioInput(state="AP", district="Vizag", latitude=100, longitude=83, impactRadius=80)
    with pytest.raises(ValidationError):
        ScenarioInput(state="AP", district="Vizag", latitude=17, longitude=83, windSpeed=-1, impactRadius=80)
    with pytest.raises(ValidationError):
        ScenarioInput(state="AP", district="Vizag", latitude=17, longitude=83, rainfall=-10, impactRadius=80)
    with pytest.raises(ValidationError):
        ScenarioInput(state="AP", district="Vizag", latitude=17, longitude=83, impactRadius=0)


def test_scenario_validation_valid():
    s = ScenarioInput(state="AP", district="Vizag", latitude=17.6, longitude=83.2, impactRadius=80)
    assert s.impactRadius > 0