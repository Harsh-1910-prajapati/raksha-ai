"""Elevation driven risk contribution (drainage / flood deepening proxy)."""

from __future__ import annotations

from app.utils.geo import clamp, normalize


def elevation_risk(elevation_m: float, coastal_proxy: float) -> tuple[float, list[str]]:
    score = clamp(
        0.6 * (100.0 - normalize(elevation_m, 0.0, 100.0)) + 0.4 * coastal_proxy * 100.0
    )
    factors: list[str] = []
    if elevation_m <= 10:
        factors.append(f"Very low elevation ({elevation_m:.0f} m)")
    elif elevation_m <= 30:
        factors.append(f"Low elevation ({elevation_m:.0f} m)")
    elif elevation_m > 100:
        factors.append(f"Raised terrain ({elevation_m:.0f} m) — lower drainage risk")
    if coastal_proxy >= 0.6:
        factors.append("Coastal lowland exposure")
    return round(score, 1), factors