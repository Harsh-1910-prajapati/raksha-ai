"""GeminiProvider abstraction.

GeminiProvider calls the live Gemini API. MockGeminiProvider generates
deterministic, structured decision-support text locally so the whole product
remains runnable without credentials.
"""

from __future__ import annotations

import abc
from typing import Any

from app.risk_engine import risk_level  # noqa: F401  (re-exported for builders)


class GeminiProvider(abc.ABC):
    name: str = "base"
    note: str = ""

    @abc.abstractmethod
    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def action_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def alert(self, context: dict[str, Any], alert_type: str) -> dict[str, Any]:
        ...

    @abc.abstractmethod
    def state_brief(self, context: dict[str, Any]) -> dict[str, Any]:
        ...


def build_context(simulation: dict[str, Any]) -> dict[str, Any]:
    """Structured, risk-engine-first context passed to the AI.

    Numeric risk scores always come from the deterministic risk engine; the AI is
    asked to reason over them, never to produce them.
    """
    risk = simulation["risk"]
    overall = risk["overall"]
    scenario = simulation["scenario"]
    infra_items = simulation["infrastructure"]["items"]
    zones = simulation["zones"]

    critical_infra = [
        {
            "name": i["name"],
            "type": i["type"],
            "risk": i["riskScore"],
            "level": i["riskLevel"],
            "threats": i.get("threats", []),
            "recommendation": i.get("recommendation", ""),
            "priority": i.get("priority", 3),
        }
        for i in infra_items
        if i["riskScore"] >= 50
    ]

    return {
        "disaster": scenario["disasterType"],
        "disasterName": {
            "CYCLONE": "Cyclone",
            "FLOOD": "Flood",
            "EXTREME_RAINFALL": "Extreme Rainfall",
        }.get(scenario["disasterType"], scenario["disasterType"]),
        "location": f"{scenario['district']}, {scenario['state']}",
        "district": scenario["district"],
        "state": scenario["state"],
        "windSpeed": scenario["windSpeed"],
        "rainfall": scenario["rainfall"],
        "stormSurge": scenario["stormSurge"],
        "impactRadius": scenario["impactRadius"],
        "durationHours": scenario["durationHours"],
        "overallRisk": overall["score"],
        "riskLevel": overall["level"],
        "components": {
            k: {"score": c["score"], "level": c["level"], "factors": c["factors"]}
            for k, c in risk["components"].items()
        },
        "populationExposed": risk["exposure"]["populationExposed"],
        "exposureAreaSqKm": risk["exposure"]["areaSqKm"],
        "highRiskAreas": [
            {
                "label": z["label"],
                "riskScore": z["riskScore"],
                "riskLevel": z["riskLevel"],
                "factors": z["factors"],
                "elevationM": z["elevationM"],
            }
            for z in zones
            if z["riskLevel"] in {"HIGH", "CRITICAL"}
        ],
        "criticalInfrastructure": critical_infra,
        "infrastructureCount": {
            t: cnt for t, cnt in simulation["infrastructure"]["counts"].items()
        },
        "accessibilityIssues": [
            f
            for c in risk["components"].values()
            if c["name"].lower() == "accessibility risk"
            for f in c["factors"]
        ],
    }


JSON_SCHEMA_NOTE = (
    "Return ONLY valid JSON matching the requested schema. Do not include "
    "markdown, explanations, or any text outside the JSON object."
)