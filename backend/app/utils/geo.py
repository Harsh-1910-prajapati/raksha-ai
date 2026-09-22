"""Geospatial helpers used across the risk engine."""

from __future__ import annotations

import math
from typing import Iterable

EARTH_RADIUS_KM = 6371.0088


def haversine_km(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> float:
    """Great-circle distance in kilometres between two coordinates."""
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def offset_point(
    lat: float, lon: float, dist_km: float, bearing_deg: float
) -> tuple[float, float]:
    """Destination coordinate at dist_km along bearing_deg (degrees)."""
    bearing = math.radians(bearing_deg)
    d_over_r = dist_km / EARTH_RADIUS_KM
    lat_r = math.radians(lat)
    lon_r = math.radians(lon)

    lat2 = math.asin(
        math.sin(lat_r) * math.cos(d_over_r)
        + math.cos(lat_r) * math.sin(d_over_r) * math.cos(bearing)
    )
    lon2 = lon_r + math.atan2(
        math.sin(bearing) * math.sin(d_over_r) * math.cos(lat_r),
        math.cos(d_over_r) - math.sin(lat_r) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def normalize(value: float, lo: float, hi: float) -> float:
    """Map value from [lo, hi] to [0, 100], clamped beyond the range."""
    if hi <= lo:
        return 0.0
    return clamp((value - lo) / (hi - lo) * 100.0)


def deterministic_noise(seed: str) -> float:
    """Deterministic pseudo random value in [0, 1) for a string seed."""
    h = 0x811C9DC5
    for ch in seed.encode("utf-8"):
        h ^= ch
        h = (h * 0x01000193) & 0xFFFFFFFF
    return (h % 10_000) / 10_000.0


def mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)