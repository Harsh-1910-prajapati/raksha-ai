"""Scenario orchestrator.

Combines scenario parameters, geospatial context, infrastructure and the
deterministic risk engine into a single explainable RiskResult.
"""

from __future__ import annotations

import math
import uuid
from datetime import datetime, timezone

from app.infrastructure.providers import get_infrastructure_provider
from app.risk_engine import risk_level
from app.risk_engine.accessibility import accessibility_risk
from app.risk_engine.elevation import elevation_risk
from app.risk_engine.flood import flood_risk
from app.risk_engine.infrastructure import infrastructure_exposure
from app.risk_engine.overall import COMPONENT_NAMES, weights as overall_weights
from app.risk_engine.population import population_exposure
from app.risk_engine.wind import wind_risk
from app.schemas.risk import (
    Exposure,
    RiskComponent,
    RiskResult,
    ZoneRisk,
)
from app.schemas.scenario import Scenario, ScenarioInput
from app.services.geo_data import get_geo_provider
from app.utils.geo import clamp, haversine_km, offset_point


def scenario_severity(input: ScenarioInput) -> str:
    wind = input.windSpeed
    rainfall = input.rainfall
    surge = input.stormSurge

    score = 0.0
    score += min(wind / 220.0, 1.0) * 50.0
    score += min(rainfall / 400.0, 1.0) * 30.0
    score += min(surge / 4.0, 1.0) * 20.0
    if score >= 75:
        return "EXTREME"
    if score >= 50:
        return "SEVERE"
    if score >= 25:
        return "HIGH"
    return "MODERATE"


def _comp(name: str, score: float, factors: list[str], weight: float) -> RiskComponent:
    return RiskComponent(
        name=name, score=score, level=risk_level.classify(score), factors=factors, weight=weight
    )


def compute_components(
    input: ScenarioInput,
    district_ctx: dict,
    geo,
    infra_items: list[dict],
) -> tuple[dict[str, RiskComponent], dict[str, float]]:
    weights = overall_weights()

    # Flood (scenario-centre geospatial context)
    elevation = geo.elevation_at(input.latitude, input.longitude)
    coastal = geo.island_proxy(input.latitude, input.longitude)
    flood_score, flood_factors = flood_risk(
        input.rainfall,
        input.stormSurge,
        elevation,
        coastal,
        str(district_ctx.get("floodProne", "moderate")),
    )

    # Wind (infrastructure density acts as exposure modifier)
    exposure_modifier = clamp(len(infra_items) / 24.0)
    wind_score, wind_factors = wind_risk(input.windSpeed, exposure_modifier)

    # Population exposure
    pop_exposed, pop_score, pop_factors = population_exposure(
        latitude=input.latitude,
        longitude=input.longitude,
        impact_radius_km=input.impactRadius,
        scenario_override=input.populationExposure,
        district_population=int(district_ctx.get("population", 0)),
        district_area_sqkm=float(district_ctx.get("areaSqKm", 3000)),
        district_name=input.district,
        district_state=input.state,
    )

    # Infrastructure exposure
    infra_score, infra_factors = infrastructure_exposure(infra_items)

    # Accessibility
    road_items = [i for i in infra_items if i["type"] in {"road", "bridge"}]
    access_score, access_factors = accessibility_risk(
        road_items, len(infra_items), float(district_ctx.get("areaSqKm", 3000))
    )

    comps = {
        "flood": _comp("Flood Risk", flood_score, flood_factors, weights["flood"]),
        "wind": _comp("Wind Risk", wind_score, wind_factors, weights["wind"]),
        "population": _comp("Population Exposure", pop_score, pop_factors, weights["population"]),
        "infrastructure": _comp(
            "Infrastructure Exposure", infra_score, infra_factors, weights["infrastructure"]
        ),
        "accessibility": _comp("Accessibility Risk", access_score, access_factors, weights["accessibility"]),
    }
    plain = {name: comps[name].score for name in COMPONENT_NAMES}
    return comps, plain


def _attributes_for(item) -> list[float]:
    geometry = item.get("geometry") if isinstance(item, dict) else item.geometry
    path = item.get("path") if isinstance(item, dict) else item.path
    if geometry == "line" and path:
        return [float(v) for pair in path for v in pair]
    lat = item.get("latitude") if isinstance(item, dict) else item.latitude
    lon = item.get("longitude") if isinstance(item, dict) else item.longitude
    return [lat, lon]


def build_zones(
    input: ScenarioInput,
    geo,
    district_ctx: dict,
    infra_items: list[dict],
) -> list[ZoneRisk]:
    radius = input.impactRadius
    rings = [0.35, 0.65, 0.95]
    sectors = 6
    angles = [60.0 * i for i in range(sectors)]

    exposures = []
    for item in infra_items:
        attrs = _attributes_for(item)
        for i in range(0, len(attrs), 2):
            exposures.append(
                {
                    "type": item["type"],
                    "riskScore": item["riskScore"],
                    "lat": attrs[i],
                    "lon": attrs[i + 1],
                }
            )

    zones: list[ZoneRisk] = []
    for ring_i, ring in enumerate(rings):
        for angle in angles:
            dist_km = ring * radius
            if dist_km < 1.0:
                dist_km = 1.0
            plat, plon = offset_point(input.latitude, input.longitude, dist_km, angle)
            # fit placeholders
            zone = _evaluate_zone(
                input, geo, district_ctx, infra_items, exposures,
                plat, plon, dist_km, ring_i, angle,
            )
            zones.append(zone)

    # sort by score desc for stable display
    zones.sort(key=lambda z: z.riskScore, reverse=True)
    return zones


def _evaluate_zone(
    input, geo, district_ctx, infra_items, exposures, plat, plon, dist_km, ring_i, angle,
) -> ZoneRisk:
    radius = input.impactRadius or 1.0
    weights = overall_weights()

    elevation = geo.elevation_at(plat, plon)
    coastal = geo.island_proxy(plat, plon)

    flood_score, flood_factors = flood_risk(
        input.rainfall,
        input.stormSurge,
        elevation,
        coastal,
        str(district_ctx.get("floodProne", "moderate")),
    )
    wind_score, wind_factors = wind_risk(input.windSpeed, 0.0)
    elev_score, elev_factors = elevation_risk(elevation, coastal)

    # distance-decayed asset exposure for this sector
    decay_radius = max(radius * 0.35, 1.0)
    weighted: list[tuple[dict, float]] = []
    total_weight = 0.0
    for exposure in exposures:
        d = haversine_km(plat, plon, exposure["lat"], exposure["lon"])
        w = max(0.0, 1.0 - d / decay_radius)
        if w > 0:
            weighted.append((exposure, w))
            total_weight += w
    if weighted:
        infra_score = clamp(
            sum(e["riskScore"] * w for e, w in weighted) / total_weight
        )
        infra_factors = [f"{len(weighted)} assets within influence of this sector"]
    else:
        infra_score = 0.0
        infra_factors = ["No modelled assets in this sector"]

    pop_score = clamp(total_weight / 3.0 * 100.0)
    access_score = clamp(100.0 - elevation + (len(road_type_exposures(exposures)) * 5.0))
    if not weighted:
        access_factors = ["No modelled assets in this sector"]
    else:
        access_factors = [f"{len(weighted)} assets in this sector"]

    proximity = clamp(100.0 * max(0.0, 1.0 - dist_km / max(radius * 0.7, 1.0)))

    plain = {
        "flood": flood_score,
        "wind": wind_score * 0.8 + proximity * 0.2,
        "population": pop_score,
        "infrastructure": infra_score,
        "accessibility": access_score,
    }
    # ensure self explanation for zones is coherent
    overall = sum(plain[name] * weights[name] for name in COMPONENT_NAMES)
    overall = clamp(overall * 0.6 + proximity * 0.4)

    factors: list[str] = []
    if flood_score >= 60:
        factors.append(f"Elevated flood potential ({flood_score:.0f})")
    if elevation <= 15:
        factors.append(f"Low elevation (~{elevation:.0f} m)")
    if coastal >= 0.7:
        factors.append("Coastal exposure")
    if proximity >= 60:
        factors.append(f"{dist_km:.0f} km from cyclone scenario centre")
    if infra_score >= 55:
        factors.append("Critical assets located in this sector")
    if not factors:
        factors.append("Relatively protected sector")

    level = risk_level.classify(overall)
    compass = COMPASS[int(angle) % len(COMPASS)]
    return ZoneRisk(
        id=f"zone-r{ring_i + 1}-{compass.lower()}",
        label=f"Sector {compass} · {dist_km:.0f} km",
        latitude=round(plat, 5),
        longitude=round(plon, 5),
        distanceKm=round(dist_km, 1),
        elevationM=round(elevation, 1),
        riskScore=round(overall, 1),
        riskLevel=level,
        components=plain,
        factors=factors,
    )


COMPASS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]


def road_type_exposures(exposures: list[dict]) -> list[dict]:
    return [e for e in exposures if e.get("type") in {"road", "bridge"}]


def run_scenario(input: ScenarioInput) -> dict:
    geo = get_geo_provider()
    district_ctx = geo.district_context(input.state, input.district)

    infra_provider = get_infrastructure_provider()
    infra_set = infra_provider.list_for(
        input.state,
        input.district,
        input.latitude,
        input.longitude,
        input.impactRadius,
        {
            "windSpeed": input.windSpeed,
            "rainfall": input.rainfall,
            "stormSurge": input.stormSurge,
            "impactRadius": input.impactRadius,
        },
    )

    infra_dicts = [
        {
            "name": i.name,
            "type": i.type.value,
            "riskScore": i.riskScore,
            "riskLevel": i.riskLevel,
            "latitude": i.latitude,
            "longitude": i.longitude,
            "path": i.path,
            "geometry": i.geometry,
        }
        for i in infra_set.items
    ]

    comps, plain = compute_components(input, district_ctx, geo, infra_dicts)
    overall_score = sum(plain[name] * overall_weights()[name] for name in COMPONENT_NAMES)
    overall_score = round(clamp(overall_score), 1)

    zones = build_zones(input, geo, district_ctx, infra_dicts)

    pop_exposed, pop_score, _ = population_exposure(
        latitude=input.latitude,
        longitude=input.longitude,
        impact_radius_km=input.impactRadius,
        scenario_override=input.populationExposure,
        district_population=int(district_ctx.get("population", 0)),
        district_area_sqkm=float(district_ctx.get("areaSqKm", 3000)),
        district_name=input.district,
        district_state=input.state,
    )
    circle_area = math.pi * input.impactRadius**2
    area = min(circle_area, float(district_ctx.get("areaSqKm", circle_area)))

    high_risk_zones = [z for z in zones if z.riskLevel in {"HIGH", "CRITICAL"}]
    severity = scenario_severity(input)

    scenario = Scenario(
        id=uuid.uuid4().hex[:12],
        disasterType=input.disasterType,
        state=input.state,
        district=input.district,
        latitude=input.latitude,
        longitude=input.longitude,
        windSpeed=input.windSpeed,
        rainfall=input.rainfall,
        stormSurge=input.stormSurge,
        impactRadius=input.impactRadius,
        durationHours=input.durationHours,
        populationExposure=input.populationExposure,
        severity=severity,
        createdAt=datetime.now(timezone.utc).isoformat(),
    )

    result = RiskResult(
        disasterType=input.disasterType.value,
        state=input.state,
        district=input.district,
        overall={
            "score": overall_score,
            "level": risk_level.classify(overall_score),
            "weights": overall_weights(),
            "label": "RakshaAI Prototype Risk Index",
        },
        components=comps,
        exposure=Exposure(
            populationExposed=pop_exposed,
            populationRiskScore=round(pop_score, 1),
            areaSqKm=round(area, 1),
            severityLabel=severity,
        ),
        zones=zones,
    )

    return {
        "disasterType": input.disasterType.value,
        "state": input.state,
        "district": input.district,
        "scenario": scenario.model_dump(mode="json"),
        "risk": result.model_dump(mode="json"),
        "zones": [z.model_dump(mode="json") for z in zones],
        "highRiskAreas": [
            {
                "label": z.label,
                "latitude": z.latitude,
                "longitude": z.longitude,
                "riskScore": z.riskScore,
                "riskLevel": z.riskLevel,
                "factors": z.factors,
            }
            for z in high_risk_zones
        ],
        "infrastructure": infra_set.model_dump(mode="json"),
        "exposure": result.exposure.model_dump(mode="json"),
        "geoProvider": geo.status(),
        "infraProvider": infra_provider.status(),
    }