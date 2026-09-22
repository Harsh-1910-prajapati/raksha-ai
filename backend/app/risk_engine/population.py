"""Population exposure scoring (deterministic estimate).

Uses the district population and the fraction of the impact area lying inside
the district. populationExposure from the scenario overrides the estimate when
> 0.
"""

from __future__ import annotations

import math

from app.services.geo_data import get_district_by_proximity
from app.utils.geo import clamp


def _area_fraction(impact_radius_km: float, district_area_sqkm: float) -> float:
    if district_area_sqkm <= 0:
        return 1.0
    circle_area = math.pi * max(impact_radius_km, 0.0) ** 2
    return clamp(circle_area / district_area_sqkm, 0.1, 1.9) / 1.9


def population_exposure(
    latitude: float,
    longitude: float,
    impact_radius_km: float,
    scenario_override: float,
    district_population: int,
    district_area_sqkm: float,
    district_name: str,
    district_state: str,
) -> tuple[int, float, list[str]]:
    if scenario_override > 0:
        exposed = int(round(scenario_override))
    else:
        fraction = _area_fraction(impact_radius_km, district_area_sqkm)
        exposed = int(round(district_population * fraction))

    # Log-scaled population risk so very large cities do not dominate linearly.
    population_score = clamp((math.log10(max(exposed, 1)) / math.log10(10_000_000)) * 100.0)

    factors: list[str] = []
    if exposed >= 1_000_000:
        factors.append(f"Very high population exposure (~{exposed / 1_000_000:.2f}M)")
    elif exposed >= 200_000:
        factors.append(f"High population exposure (~{exposed // 1000}K)")
    elif exposed > 0:
        factors.append(f"Moderate population exposure (~{exposed // 1000}K)")
    else:
        factors.append("Population data unavailable — using minimal estimate")
    return exposed, round(population_score, 1), factors