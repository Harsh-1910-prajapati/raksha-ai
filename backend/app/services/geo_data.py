"""GeoDataProvider abstraction.

Frontend → Backend API → GeoDataProvider (Earth Engine or Demo).

EarthEngineProvider activates only when Earth Engine credentials are
configured (EARTH_ENGINE_ENABLED=1 plus a project/account). Otherwise the
DemoGeoDataProvider is used so the application always runs.
"""

from __future__ import annotations

import abc
import math

from app.config import get_settings
from app.services.locations import get_district
from app.utils.geo import clamp, deterministic_noise, normalize

try:  # pragma: no cover - optional dependency
    import ee  # type: ignore

    _EE_AVAILABLE = True
except Exception:  # pragma: no cover
    ee = None
    _EE_AVAILABLE = False


class GeoDataProvider(abc.ABC):
    """Interface for geospatial/environmental data."""

    name: str = "base"

    @abc.abstractmethod
    def elevation_at(self, latitude: float, longitude: float) -> float:
        """Return approximate elevation in metres above sea level."""

    @abc.abstractmethod
    def island_proxy(self, latitude: float, longitude: float) -> float:
        """0 (open terrain) .. 1 (strong coastal exposure)."""

    @abc.abstractmethod
    def district_context(self, state: str, district: str) -> dict:
        """Contextual district metadata."""

    @abc.abstractmethod
    def status(self) -> dict:
        """Provider availability description."""


class DemoGeoDataProvider(GeoDataProvider):
    """Deterministic demo geospatial provider using the location catalogue.

    Elevation is interpolated around the district's mean elevation plus a
    deterministic local variation so results are reproducible per coordinate.
    """

    name = "demo"

    def elevation_at(self, latitude: float, longitude: float) -> float:
        district = get_district_by_proximity(latitude, longitude)
        base = float(district.get("meanElevationM", 30)) if district else 30.0
        variation = deterministic_noise(f"elev:{latitude:.4f}:{longitude:.4f}")
        coastal = district.get("coastal", False) if district else False
        if coastal:
            base = min(base, 45.0)
        local = base + (variation - 0.5) * 18.0
        return round(clamp(local, 0.0, 4000.0), 1)

    def island_proxy(self, latitude: float, longitude: float) -> float:
        district = get_district_by_proximity(latitude, longitude)
        if not district:
            return 0.2
        if not district.get("coastal", False):
            return 0.1
        base = {"critical": 0.95, "high": 0.8, "moderate": 0.6}.get(
            district.get("floodProne", "moderate"), 0.5
        )
        nudge = deterministic_noise(f"island:{latitude:.4f}:{longitude:.4f}")
        return round(clamp(base + (nudge - 0.5) * 0.2, 0.0, 1.0), 2)

    def district_context(self, state: str, district: str) -> dict:
        data = get_district(state, district)
        if data is None:
            return {
                "state": state,
                "district": district,
                "meanElevationM": 30,
                "coastal": False,
                "floodProne": "unknown",
                "population": 0,
                "populationSqKm": 300,
                "areaSqKm": 3000,
                "demo": True,
            }
        return {**data, "demo": True}

    def status(self) -> dict:
        return {
            "provider": self.name,
            "available": True,
            "elevationSource": "District mean elevation interpolation (DEMO DATA)",
        }


class EarthEngineProvider(GeoDataProvider):
    """Earth Engine backed provider (elevation via SRTM).

    Activate with EARTH_ENGINE_ENABLED=1, EARTH_ENGINE_PROJECT and (for service
    accounts) EARTH_ENGINE_SERVICE_ACCOUNT. The Earth Engine Python client must
    be installed (pip install earthengine-api).
    """

    name = "earth-engine"

    def __init__(self) -> None:
        settings = get_settings()
        self.project = settings.earth_engine_project or settings.google_cloud_project
        self.account = settings.earth_engine_account
        self.enabled = settings.earth_engine_enabled and _EE_AVAILABLE and bool(self.project)
        self._initialized = False

    def _init_ee(self) -> None:  # pragma: no cover - requires live credentials
        if ee is None:
            raise RuntimeError("Earth Engine Python client not installed")
        if not self._initialized:
            if self.account:
                credentials = ee.ServiceAccountCredentials(self.account)
            else:
                credentials = "persistent"
            ee.Initialize(project=self.project, credentials=credentials)
            self._initialized = True

    def elevation_at(self, latitude: float, longitude: float) -> float:
        if not self.enabled:
            raise RuntimeError("Earth Engine provider is not enabled")
        try:
            self._init_ee()
            point = ee.Geometry.Point([longitude, latitude])
            image = ee.Image("NASA/SRTMGL1_003").select("elevation")
            sampled = image.sample(point, 30).first().get("elevation")
            return float(sampled.getInfo())  # type: ignore
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Earth Engine query failed: {exc}") from exc

    def island_proxy(self, latitude: float, longitude: float) -> float:  # pragma: no cover
        return 0.5  # refined in a future iteration from coastal distance

    def district_context(self, state: str, district: str) -> dict:
        return get_district(state, district) or {}

    def status(self) -> dict:
        return {
            "provider": self.name,
            "available": self.enabled,
            "source": "NASA SRTM (elevation)",
            "project": self.project or "(not set)",
        }


def get_geo_provider() -> GeoDataProvider:
    settings = get_settings()
    if settings.earth_engine_enabled and _EE_AVAILABLE:
        candidate = EarthEngineProvider()
        if candidate.enabled:
            return candidate
    return DemoGeoDataProvider()


_PROXIMITY_CACHE: dict[tuple[str, str], dict] = {}


def get_district_by_proximity(latitude: float, longitude: float) -> dict:
    """Nearest catalogue district, cached."""
    from app.services.locations import _load

    key = (f"{latitude:.2f}", f"{longitude:.2f}")
    if key in _PROXIMITY_CACHE:
        return _PROXIMITY_CACHE[key]
    best: dict | None = None
    best_dist = float("inf")
    for state in _load().get("states", []):
        for d in state.get("districts", []):
            dlat = d["latitude"] - latitude
            dlon = d["longitude"] - longitude
            dist = math.hypot(dlat, dlon)
            if dist < best_dist:
                best_dist = dist
                best = {**d, "state": state["name"]}
    result = best or {}
    if len(_PROXIMITY_CACHE) < 512:
        _PROXIMITY_CACHE[key] = result
    return result