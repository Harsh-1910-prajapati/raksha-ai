"""Location catalogue loaded from data files (data/disaster_types.json, data/locations.json)."""

from __future__ import annotations

import json
from typing import Any

from app.config import DATA_DIR


def _load() -> dict[str, Any]:
    path = DATA_DIR / "locations.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _disaster_types() -> dict[str, Any]:
    path = DATA_DIR / "disaster_types.json"
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def get_states() -> list[dict[str, Any]]:
    return [
        {"id": s["id"], "name": s["name"], "coastal": s.get("coastal", False)}
        for s in _load().get("states", [])
    ]


def get_districts(state: str) -> list[dict[str, Any]]:
    for s in _load().get("states", []):
        if s["name"].lower() == state.lower():
            return [
                {
                    "id": d["id"],
                    "name": d["name"],
                    "latitude": d["latitude"],
                    "longitude": d["longitude"],
                }
                for d in s.get("districts", [])
            ]
    return []


def get_district(state: str, district: str) -> dict[str, Any] | None:
    for s in _load().get("states", []):
        if s["name"].lower() != state.lower():
            continue
        for d in s.get("districts", []):
            if d["name"].lower() == district.lower():
                return {**d, "state": s["name"]}
    return None


def get_disaster_types() -> dict[str, Any]:
    return _disaster_types()


def state_exists(state: str) -> bool:
    return any(s["name"].lower() == state.lower() for s in _load().get("states", []))