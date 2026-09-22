"""Overall risk combination with configurable, documented weights.

    overall = flood*wF + wind*wW + population*wP + infrastructure*wI + accessibility*wA
"""

from __future__ import annotations

from app.config import get_settings
from app.utils.geo import clamp

COMPONENT_NAMES = ("flood", "wind", "population", "infrastructure", "accessibility")


def weights() -> dict[str, float]:
    s = get_settings()
    return {
        "flood": s.risk_flood_weight,
        "wind": s.risk_wind_weight,
        "population": s.risk_population_weight,
        "infrastructure": s.risk_infrastructure_weight,
        "accessibility": s.risk_accessibility_weight,
    }


def overall_risk(components: dict[str, float]) -> float:
    w = weights()
    score = sum(components[name] * w[name] for name in COMPONENT_NAMES)
    return round(clamp(score), 1)