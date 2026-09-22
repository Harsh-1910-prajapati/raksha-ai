"""Risk-engine output schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RiskFactor(BaseModel):
    label: str
    value: str
    weight: float = Field(0.0, ge=0, le=1)


class RiskComponent(BaseModel):
    name: str
    score: float = Field(..., ge=0, le=100)
    level: str
    factors: list[str] = Field(default_factory=list)
    weight: float = Field(default_factory=lambda: 0.0, alias="weight")


class RiskSummary(BaseModel):
    score: float = Field(..., ge=0, le=100)
    level: str
    components: dict[str, RiskComponent]
    weights: dict[str, float]
    label: str = "RakshaAI Prototype Risk Index"
    weightsNote: str = (
        "Prototype weighting is used for demonstration. It is not an official "
        "government or scientific formula."
    )


class Exposure(BaseModel):
    populationExposed: int
    populationRiskScore: float = Field(..., ge=0, le=100)
    areaSqKm: float
    severityLabel: str
    sourcesNote: str = "Estimates are modelled from demo district data."


class ZoneRisk(BaseModel):
    id: str
    label: str
    latitude: float
    longitude: float
    distanceKm: float
    elevationM: float
    riskScore: float = Field(..., ge=0, le=100)
    riskLevel: str
    components: dict[str, float]
    factors: list[str]


class OverallRisk(BaseModel):
    score: float = Field(..., ge=0, le=100)
    level: str
    weights: dict[str, float]
    label: str = "RakshaAI Prototype Risk Index"


class RiskResult(BaseModel):
    disasterType: str
    state: str
    district: str
    overall: OverallRisk
    components: dict[str, RiskComponent]
    exposure: Exposure
    zones: list[ZoneRisk]
    inferenceNote: str = (
        "Decision-support estimate computed by the RakshaAI prototype risk engine. "
        "Not an official government forecast or warning."
    )