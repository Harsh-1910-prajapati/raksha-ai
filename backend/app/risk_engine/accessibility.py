"""Accessibility risk: how reachable the impacted area and its lifelines are."""

from __future__ import annotations

from app.utils.geo import clamp


def accessibility_risk(
    road_items: list[dict],
    total_items: int,
    district_area_sqkm: float,
) -> tuple[float, list[str]]:
    high_risk_roads = [r for r in road_items if r["riskScore"] >= 60]
    road_density = len(road_items) / max(district_area_sqkm, 1.0)

    density_score = clamp(100 - normalize_density(road_density))
    disruption_score = clamp((len(high_risk_roads) / max(len(road_items), 1)) * 100.0)

    score = clamp(0.55 * density_score + 0.45 * disruption_score)
    if not road_items:
        score = clamp(score + 15.0, 0, 100)

    factors: list[str] = []
    if density_score >= 55:
        factors.append("Limited alternate road access in impact area")
    if high_risk_roads and len(road_items) >= 3:
        factors.append(
            f"{len(high_risk_roads)} of {len(road_items)} road links at high risk"
        )
    if not road_items:
        factors.append("Road network data sparse for this zone")
    return round(score, 1), factors


def normalize_density(density: float) -> float:
    """Road density per sqkm → 0-100 (saturating around 0.02 links/km²)."""
    return (density / 0.02) * 100.0