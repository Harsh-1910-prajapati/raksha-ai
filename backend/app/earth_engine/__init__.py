"""Geospatial/environmental data provider (Earth Engine adapter).

Kept as a thin service that mostly delegates to app.services.geo_data. This
module documents how satellite/environmental datasets plug into the platform.
"""

from __future__ import annotations

from app.services.geo_data import get_geo_provider  # noqa: F401

__all__ = ["get_geo_provider"]