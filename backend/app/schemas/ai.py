"""AI (Gemini / mock) response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AIAnalysis(BaseModel):
    ai_provider: str = Field(..., description='"gemini" or "mock"')
    provider_note: str = ""
    summary: str = ""
    priorityAreas: list[str] = Field(default_factory=list)
    infrastructureRisks: list[str] = Field(default_factory=list)
    recommendedActions: list[str] = Field(default_factory=list)
    resourcePriorities: list[str] = Field(default_factory=list)
    evacuationConsiderations: list[str] = Field(default_factory=list)
    communicationGuidance: list[str] = Field(default_factory=list)


class ActionPlan(BaseModel):
    ai_provider: str = Field(..., description='"gemini" or "mock"')
    provider_note: str = ""
    immediateActions: list[str] = Field(default_factory=list)
    beforeImpact: list[str] = Field(default_factory=list)
    duringEvent: list[str] = Field(default_factory=list)
    recovery: list[str] = Field(default_factory=list)


class AlertLanguage(BaseModel):
    language: str
    language_name: str
    title: str
    body: str


class AlertContent(BaseModel):
    ai_provider: str = Field(..., description='"gemini" or "mock"')
    provider_note: str = ""
    alert_type: str = Field(..., description='"authority" or "citizen"')
    title: str
    summary: str
    languages: list[AlertLanguage]
    disclaimer: str = Field(
        default=(
            "RakshaAI is a prototype decision-support system. Follow instructions "
            "from local authorities and official disaster agencies."
        )
    )


class StateBrief(BaseModel):
    ai_provider: str = Field(..., description='"gemini" or "mock"')
    provider_note: str = ""
    state: str
    generatedAt: str
    affectedDistricts: list[str] = Field(default_factory=list)
    highRiskZones: list[str] = Field(default_factory=list)
    criticalInfrastructure: dict[str, int] = Field(default_factory=dict)
    hospitalsAtRisk: list[str] = Field(default_factory=list)
    sheltersAtRisk: list[str] = Field(default_factory=list)
    accessibilityIssues: list[str] = Field(default_factory=list)
    recommendedPriorities: list[str] = Field(default_factory=list)
    communicationMessage: str = ""
    disclaimer: str = Field(
        default=(
            "RakshaAI is a prototype decision-support system. Risk scores are "
            "model-generated estimates and should not replace official forecasts, "
            "warnings, or emergency-management instructions."
        )
    )