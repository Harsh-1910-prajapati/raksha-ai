"""Scenario request/response schemas."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator


class DisasterType(str, Enum):
    CYCLONE = "CYCLONE"
    FLOOD = "FLOOD"
    EXTREME_RAINFALL = "EXTREME_RAINFALL"


class ScenarioInput(BaseModel):
    disasterType: DisasterType = DisasterType.CYCLONE
    state: str = Field(..., min_length=2, max_length=100)
    district: str = Field(..., min_length=2, max_length=100)
    latitude: float = Field(..., description="WGS84 latitude")
    longitude: float = Field(..., description="WGS84 longitude")
    windSpeed: float = Field(0.0, description="maximum wind speed in km/h")
    rainfall: float = Field(0.0, description="projected rainfall in mm")
    stormSurge: float = Field(0.0, description="storm surge height in metres")
    impactRadius: float = Field(..., gt=0, description="impact radius in km")
    durationHours: float = Field(12.0, ge=1, le=168, description="scenario duration in hours")
    populationExposure: float = Field(
        0.0, ge=0, description="estimated population exposed (used as override when set)"
    )

    @field_validator("latitude")
    @classmethod
    def _lat_in_range(cls, v: float) -> float:
        if not -90.0 <= v <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        return v

    @field_validator("longitude")
    @classmethod
    def _lon_in_range(cls, v: float) -> float:
        if not -180.0 <= v <= 180.0:
            raise ValueError("longitude must be between -180 and 180")
        return v

    @field_validator("windSpeed")
    @classmethod
    def _wind_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("wind speed cannot be negative")
        return v

    @field_validator("rainfall")
    @classmethod
    def _rain_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("rainfall cannot be negative")
        return v

    @field_validator("stormSurge")
    @classmethod
    def _surge_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("storm surge cannot be negative")
        return v


class Scenario(BaseModel):
    id: str
    disasterType: DisasterType
    state: str
    district: str
    latitude: float
    longitude: float
    windSpeed: float
    rainfall: float
    stormSurge: float
    impactRadius: float
    durationHours: float
    populationExposure: float
    severity: str
    createdAt: str
    sourceLabel: str = "Scenario / forecast input (not an official track)"