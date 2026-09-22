"""Prototype wind risk scoring.

Wind speed normalized to a severe-cyclone scale plus an exposure modifier.
"""

from __future__ import annotations

from app.utils.geo import clamp, normalize


def wind_risk(wind_speed_kmh: float, exposure_modifier: float = 0.0) -> tuple[float, list[str]]:
    wind_score = normalize(wind_speed_kmh, 0.0, 220.0)
    score = clamp(0.85 * wind_score + 0.15 * clamp(exposure_modifier * 100.0))
    if wind_speed_kmh <= 10 and exposure_modifier <= 0.05:
        score = 0.0

    factors: list[str] = []
    if wind_speed_kmh >= 118:
        factors.append(f"Very high wind speed ({wind_speed_kmh:.0f} km/h, cyclonic)")
    elif wind_speed_kmh >= 62:
        factors.append(f"High wind speed ({wind_speed_kmh:.0f} km/h)")
    elif wind_speed_kmh > 0:
        factors.append(f"Elevated wind speed ({wind_speed_kmh:.0f} km/h)")
    if exposure_modifier >= 0.6:
        factors.append("Dense exposed infrastructure")
    elif exposure_modifier >= 0.3:
        factors.append("Moderate infrastructure exposure")

    return round(score, 1), factors