"""Prototype flood risk scoring.

Deterministic combination of rainfall, storm surge, elevation and coastal
exposure. Not an official hydrological model.
"""

from __future__ import annotations

from app.utils.geo import clamp, normalize


def flood_risk(
    rainfall_mm: float,
    storm_surge_m: float,
    elevation_m: float,
    coastal_proxy: float,
    flood_prone: str,
) -> tuple[float, list[str]]:
    rainfall_score = normalize(rainfall_mm, 0.0, 400.0)
    surge_score = normalize(storm_surge_m, 0.0, 4.0)
    elevation_score = 100.0 - normalize(elevation_m, 0.0, 80.0)
    coastal_score = coastal_proxy * 100.0

    prone_bonus = {"critical": 12.0, "high": 8.0, "moderate": 4.0, "unknown": 2.0}.get(
        flood_prone, 2.0
    )

    score = clamp(
        rainfall_score * 0.33
        + surge_score * 0.27
        + elevation_score * 0.20
        + coastal_score * 0.20
        + prone_bonus
    )

    factors = []
    if rainfall_mm >= 150:
        factors.append(f"High projected rainfall ({rainfall_mm:.0f} mm)")
    elif rainfall_mm > 0:
        factors.append(f"Moderate rainfall ({rainfall_mm:.0f} mm)")
    if storm_surge_m >= 1.0:
        factors.append(f"Storm surge exposure ({storm_surge_m:.1f} m)")
    if elevation_m <= 15:
        factors.append(f"Low elevation ({elevation_m:.0f} m)" if elevation_m else "Very low elevation")
    elif elevation_m <= 40:
        factors.append(f"Below-average elevation ({elevation_m:.0f} m)")
    if coastal_proxy >= 0.7:
        factors.append("High coastal / sea exposure")
    if flood_prone in {"high", "critical"}:
        factors.append(f"District classified flood-prone ({flood_prone})")

    return round(score, 1), factors