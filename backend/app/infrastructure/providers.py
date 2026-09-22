"""Infrastructure providers.

DemoInfrastructureProvider deterministically generates plausible demo assets
around a district centre. FirebaseInfrastructureProvider is a stub that can read
from Firestore once credentials are configured.
"""

from __future__ import annotations

import abc
import math
from typing import Any

from app.config import get_settings
from app.risk_engine import risk_level
from app.schemas.infra import InfraType, InfrastructureItem, InfrastructureSet
from app.services.geo_data import get_geo_provider
from app.utils.geo import clamp, deterministic_noise, haversine_km, offset_point


class InfrastructureProvider(abc.ABC):
    name = "base"

    @abc.abstractmethod
    def list_for(
        self, state: str, district: str, lat: float, lon: float, radius_km: float, scenario: dict
    ) -> InfrastructureSet:
        ...

    @abc.abstractmethod
    def status(self) -> dict:
        ...


ROAD_TYPES = {"road"}


class DemoInfrastructureProvider(InfrastructureProvider):
    name = "demo"

    NAMES: dict[str, list[str]] = {
        "hospital": ["District Hospital", "Community Health Centre", "Corporation Hospital"],
        "shelter": ["Community Cyclone Shelter", "Cyclone Shelter (Canal Road)", "Multi-Purpose Shelter"],
        "school": ["Government High School", "Zilla Parishad School", "Girls Higher Secondary School"],
        "police": ["City Police Station", "Traffic Police Post"],
        "fire": ["Fire Station"],
        "power": ["Power Grid Substation", "Distribution Substation"],
        "water": ["Water Treatment Plant", "Overhead Water Tank"],
        "bridge": ["Bridge — State Highway link", "Canal Bridge"],
    }

    SENSITIVITY: dict[str, float] = {
        "hospital": 1.0,
        "shelter": 0.9,
        "road": 0.8,
        "bridge": 0.95,
        "power": 1.15,
        "water": 1.0,
        "school": 0.7,
        "police": 0.85,
        "fire": 1.0,
    }

    RECOMMENDATIONS: dict[str, dict[str, str]] = {
        "hospital": {
            "CRITICAL": "Move emergency supplies, verify backup power and prepare surge staffing.",
            "HIGH": "Prepare backup power and pre-position critical medicines.",
            "MODERATE": "Confirm generator fuel and staff rosters for the event window.",
        },
        "shelter": {
            "CRITICAL": "Open shelter, stock water/food/alternate power and secure roofs.",
            "HIGH": "Inspect structural integrity and pre-stock essential supplies.",
            "MODERATE": "Confirm shelter capacity and accessibility.",
        },
        "power": {
            "CRITICAL": "Protect equipment, prepare mobile generators.",
            "HIGH": "Reinforce compound and secure backup generation.",
            "MODERATE": "Monitor network load and fuel reserves.",
        },
        "water": {
            "CRITICAL": "Ensure pump backup power and alternate water supply.",
            "HIGH": "Inspect intake lines and chlorination stocks.",
            "MODERATE": "Maintain pressure and test alternate supply.",
        },
        "school": {
            "CRITICAL": "Stand by for use as temporary shelter.",
            "HIGH": "Secure loose structures and shift records to higher floors.",
            "MODERATE": "Close facilities as per authority instructions.",
        },
        "road": {
            "CRITICAL": "Deploy teams for debris clearance and route marking.",
            "HIGH": "Pre-position equipment near vulnerable culverts.",
            "MODERATE": "Monitor for inundation and restrict travel if needed.",
        },
        "bridge": {
            "CRITICAL": "Inspect structural integrity; plan alternate river crossings.",
            "HIGH": "Monitor water levels and approach approaches.",
            "MODERATE": "Conduct visual inspection before heavy movement.",
        },
        "police": {"HIGH": "Co-ordinate crowd control and route enforcement.", "MODERATE": "Maintain patrols and comms."},
        "fire": {"HIGH": "Stand by for rescue and pumping support.", "MODERATE": "Confirm equipment readiness."},
    }

    def status(self) -> dict:
        return {"provider": self.name, "available": True, "sourceLabel": "Demo data"}

    def list_for(
        self, state: str, district: str, lat: float, lon: float, radius_km: float, scenario: dict
    ) -> InfrastructureSet:
        items: list[InfrastructureItem] = []
        geo = get_geo_provider()
        district_ctx = geo.district_context(state, district)

        # Buildings / nodes
        for dtype in ["hospital", "shelter", "school", "police", "fire", "power", "water"]:
            count = 1 if dtype in {"power", "water", "fire"} else 1 if dtype == "police" else 1
            if dtype == "hospital":
                count = 2
            elif dtype == "shelter":
                count = 2
            elif dtype == "school":
                count = 2
            for i in range(count):
                items.append(
                    self._point_item(
                        dtype, state, district, lat, lon, radius_km, scenario, geo, district_ctx, i
                    )
                )

        # Road links (polylines)
        for i in range(3):
            items.append(
                self._road_item(state, district, lat, lon, radius_km, scenario, geo, district_ctx, i)
            )

        # Bridges
        for i in range(2):
            items.append(
                self._bridge_item(state, district, lat, lon, radius_km, scenario, geo, district_ctx, i)
            )

        items = [fit for fit in items if fit.riskScore is not None]
        counts: dict[str, int] = {}
        for it in items:
            counts[it.type.value] = counts.get(it.type.value, 0) + 1

        return InfrastructureSet(
            state=state,
            district=district,
            scenarioLatitude=lat,
            scenarioLongitude=lon,
            items=items,
            counts=counts,
        )

    # -- generators ---------------------------------------------------------

    def _point_item(
        self,
        dtype,
        state,
        district,
        lat,
        lon,
        radius_km,
        scenario,
        geo,
        district_ctx,
        index,
    ) -> InfrastructureItem:
        seed = f"{state}:{district}:{dtype}:{index}"
        bearing = deterministic_noise(seed + ":b") * 360.0
        dist_km = 2.0 + deterministic_noise(seed + ":d") * 11.0
        plat, plon = offset_point(lat, lon, dist_km, bearing)

        elevation = geo.elevation_at(plat, plon)
        coastal = geo.island_proxy(plat, plon)
        flood_prone = district_ctx.get("floodProne", "moderate")
        is_coastal = bool(district_ctx.get("coastal", False))

        d_from_centre = haversine_km(lat, lon, plat, plon)
        level, score = self._score_asset(
            scenario, d_from_centre, radius_km, elevation, coastal, flood_prone, is_coastal, dtype
        )
        threats = self._threats(score, flood_prone)
        name = self._name(dtype, district_ctx.get("district", district), index)
        capacity = self._capacity(dtype, index)

        return InfrastructureItem(
            id=f"{dtype}-{district.lower().replace(' ', '-')}-{index + 1:03d}",
            name=name,
            type=dtype,
            state=state,
            district=district,
            latitude=round(plat, 4),
            longitude=round(plon, 4),
            capacity=capacity,
            riskScore=score,
            riskLevel=level,
            threats=threats,
            recommendation=self.RECOMMENDATIONS.get(dtype, {}).get(level, "Monitor and prepare as instructed."),
            priority=self._priority(level, dtype),
        )

    def _road_item(self, state, district, lat, lon, radius_km, scenario, geo, district_ctx, index) -> InfrastructureItem:
        seed = f"{state}:{district}:road:{index}"
        bearing = 60.0 * index + deterministic_noise(seed + ":b") * 30.0
        dist_km = 3.0 + index * 3.0
        p1 = offset_point(lat, lon, dist_km, bearing)
        p2 = offset_point(lat, lon, dist_km + 6.0, bearing + 15.0)

        mid = offset_point(lat, lon, dist_km + 3.0, bearing + 7.5)
        elevation = geo.elevation_at(mid[0], mid[1])
        coastal = geo.island_proxy(mid[0], mid[1])
        d_from_centre = haversine_km(lat, lon, mid[0], mid[1])
        level, score = self._score_asset(
            scenario, d_from_centre, radius_km, elevation, coastal,
            district_ctx.get("floodProne", "moderate"), bool(district_ctx.get("coastal", False)), "road",
        )
        threat = self._threats(score, district_ctx.get("floodProne", "moderate"))
        name = self._name("road", district, index)
        return InfrastructureItem(
            id=f"road-{district.lower().replace(' ', '-')}-{index + 1:03d}",
            name=name,
            type=InfraType.ROAD,
            state=state,
            district=district,
            latitude=round(mid[0], 4),
            longitude=round(mid[1], 4),
            capacity=None,
            riskScore=score,
            riskLevel=level,
            threats=threat,
            recommendation=self.RECOMMENDATIONS.get("road", {}).get(level, "Monitor route conditions."),
            priority=self._priority(level, "road"),
            geometry="line",
            path=[[round(p1[0], 4), round(p1[1], 4)], [round(p2[0], 4), round(p2[1], 4)]],
        )

    def _bridge_item(self, state, district, lat, lon, radius_km, scenario, geo, district_ctx, index) -> InfrastructureItem:
        seed = f"{state}:{district}:bridge:{index}"
        bearing = 200.0 + index * 90.0 + deterministic_noise(seed + ":b") * 20.0
        dist_km = 6.0 + index * 4.0
        plat, plon = offset_point(lat, lon, dist_km, bearing)
        elevation = max(geo.elevation_at(plat, plon) - deterministic_noise(seed + ":e") * 8, 0.5)
        coastal = geo.island_proxy(plat, plon)
        d_from_centre = haversine_km(lat, lon, plat, plon)
        level, score = self._score_asset(
            scenario, d_from_centre, radius_km, elevation, coastal,
            district_ctx.get("floodProne", "moderate"), bool(district_ctx.get("coastal", False)), "bridge",
        )
        return InfrastructureItem(
            id=f"bridge-{district.lower().replace(' ', '-')}-{index + 1:03d}",
            name=self._name("bridge", district, index),
            type=InfraType.BRIDGE,
            state=state,
            district=district,
            latitude=round(plat, 4),
            longitude=round(plon, 4),
            capacity=None,
            riskScore=score,
            riskLevel=level,
            threats=self._threats(score, district_ctx.get("floodProne", "moderate")),
            recommendation=self.RECOMMENDATIONS.get("bridge", {}).get(level, "Monitor crossing conditions."),
            priority=self._priority(level, "bridge"),
        )

    # -- helpers -------------------------------------------------------------

    def _score_asset(self, scenario, d_from_centre, radius_km, elevation_m, coastal_proxy, flood_prone, is_coastal, dtype) -> tuple[str, float]:
        rainfall = float(scenario.get("rainfall", 0))
        surge = float(scenario.get("stormSurge", 0))
        wind = float(scenario.get("windSpeed", 0))

        proximity = clamp(100 * max(0.0, 1 - d_from_centre / max(radius_km, 1.0)), 0, 100)
        flood = risk_level_components_flood(rainfall, surge, elevation_m, coastal_proxy, flood_prone)
        sensitivity = self.SENSITIVITY.get(dtype, 1.0)
        wind_eff = clamp(wind_normalized(wind) * sensitivity)
        if dtype in ROAD_TYPES:
            wind_eff = wind_eff * 0.7
        score = clamp(0.40 * flood + 0.30 * wind_eff + 0.30 * proximity)
        level = risk_level.classify(score)
        return level, round(score, 1)

    def _threats(self, score: float, flood_prone: str) -> list[str]:
        threats = []
        if score >= 60:
            threats.append("Flood")
            threats.append("Wind")
        elif score >= 40:
            threats.append("Flood")
        elif flood_prone in {"high", "critical"}:
            threats.append("Rising water risk")
        return threats or ["Low direct threat"]

    def _name(self, dtype: str, district: str, index: int) -> str:
        if dtype == "road":
            return f"{district} road link {index + 1}"
        names = self.NAMES.get(dtype, [])
        base = names[index % len(names)] if names else f"{dtype.title()} {index + 1}"
        return base

    def _capacity(self, dtype: str, index: int) -> int | None:
        if dtype == "hospital":
            return 400 + index * 150
        if dtype == "shelter":
            return 800 + index * 300
        if dtype == "school":
            return 900 + index * 200
        return None

    def _priority(self, level: str, dtype: str) -> int:
        if level == "CRITICAL":
            return 1
        if level == "HIGH" and dtype in {"hospital", "power", "water", "shelter"}:
            return 1
        if level == "HIGH":
            return 2
        return 3


def wind_normalized(wind_kmh: float) -> float:
    return clamp(wind_kmh / 220.0 * 100.0)


def risk_level_components_flood(
    rainfall: float, surge: float, elevation_m: float, coastal_proxy: float, flood_prone: str
) -> float:
    r = rainfall / 400.0 * 100.0
    s = surge / 4.0 * 100.0
    e = 100.0 - clamp(elevation_m / 80.0 * 100.0)
    c = coastal_proxy * 100.0
    bonus = {"critical": 12.0, "high": 8.0, "moderate": 4.0}.get(flood_prone, 2.0)
    return clamp(r * 0.33 + s * 0.27 + e * 0.20 + c * 0.20 + bonus)


class FirebaseInfrastructureProvider(InfrastructureProvider):
    """Stub for a Firestore-backed repository. Requires credentials.

    Activate by setting FIREBASE_PROJECT_ID and the Google service account
    environment (GOOGLE_APPLICATION_CREDENTIALS).
    """

    name = "firebase"

    def list_for(self, state, district, lat, lon, radius_km, scenario) -> InfrastructureSet:
        raise RuntimeError("FirebaseInfrastructureProvider is not configured")

    def status(self) -> dict:
        settings = get_settings()
        return {
            "provider": self.name,
            "available": bool(settings.firebase_project_id),
            "note": "Requires FIREBASE_PROJECT_ID and admin credentials.",
        }


def get_infrastructure_provider() -> InfrastructureProvider:
    settings = get_settings()
    if settings.firebase_project_id:
        try:
            return FirebaseInfrastructureProvider()
        except Exception:
            pass
    return DemoInfrastructureProvider()