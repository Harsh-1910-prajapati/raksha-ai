"""Infrastructure schemas."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class InfraType(str, Enum):
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    ROAD = "road"
    BRIDGE = "bridge"
    POWER = "power"
    WATER = "water"
    SCHOOL = "school"
    POLICE = "police"
    FIRE = "fire"


class InfrastructureItem(BaseModel):
    id: str
    name: str
    type: InfraType
    state: str
    district: str
    latitude: float
    longitude: float
    capacity: int | None = None
    riskScore: float = Field(..., ge=0, le=100)
    riskLevel: str
    threats: list[str] = Field(default_factory=list)
    recommendation: str = ""
    priority: int = 3
    geometry: str = "point"
    path: list[list[float]] | None = None
    sourceLabel: str = "Demo data (not official infrastructure registry)"


class InfrastructureSet(BaseModel):
    state: str
    district: str
    scenarioLatitude: float
    scenarioLongitude: float
    items: list[InfrastructureItem]
    counts: dict[str, int]
    note: str = (
        "Infrastructure shown is demo/simulation data generated for the prototype. "
        "It is not an official registry."
    )