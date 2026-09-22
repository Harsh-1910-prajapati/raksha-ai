"""Live Gemini provider implementation."""

from __future__ import annotations

import json
from typing import Any

from app.gemini.client import GeminiClientError, make_client
from app.gemini.provider import JSON_SCHEMA_NOTE, GeminiProvider, build_context


def _dump(context: dict[str, Any]) -> str:
    return json.dumps(context, indent=2, ensure_ascii=False)


class GeminiProviderImpl(GeminiProvider):
    name = "gemini"

    def __init__(self) -> None:
        self.client = make_client()
        self.model = self.client.model if self.client else "(none)"

    @property
    def available(self) -> bool:
        return self.client is not None

    def _gen(self, system_instruction: str, schema: str, temperature: float = 0.4):
        prompt = (
            f"{system_instruction}\n\n"
            f"Input context (JSON):\n{_dump(self._context)}\n\n"
            f"Required output JSON schema:\n{schema}\n\n{JSON_SCHEMA_NOTE}"
        )
        try:
            return self.client.generate_json(prompt, temperature=temperature)
        except GeminiClientError:
            raise

    # -- methods ------------------------------------------------------------

    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        self._context = context
        instruction = (
            "You are an emergency-management intelligence analyst for India. "
            "Reason over the structured risk-engine output. Do NOT invent new "
            "numerical risk scores — use the provided scores. Produce a concise, "
            "actionable situation analysis in full JSON."
        )
        schema = json.dumps(
            {
                "summary": "string: 3-4 sentence situation summary",
                "priorityAreas": ["string: highest priority areas with why"],
                "infrastructureRisks": ["string"],
                "recommendedActions": ["string"],
                "resourcePriorities": ["string"],
                "evacuationConsiderations": ["string"],
                "communicationGuidance": ["string"],
            }
        )
        return self._gen(instruction, schema)

    def action_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        self._context = context
        instruction = (
            "You are an emergency-responder planning assistant. Build a phased "
            "emergency action plan from the structured risk-engine output. "
            "Group actions into immediate, before-impact, during-event and "
            "recovery phases. Return full JSON."
        )
        schema = json.dumps(
            {
                "immediateActions": ["string"],
                "beforeImpact": ["string"],
                "duringEvent": ["string"],
                "recovery": ["string"],
            }
        )
        return self._gen(instruction, schema, temperature=0.5)

    def alert(self, context: dict[str, Any], alert_type: str) -> dict[str, Any]:
        self._context = context
        is_authority = alert_type == "authority"
        role = (
            "an SDMA/DM authority briefing writer"
            if is_authority
            else "a public-safety communicator for citizens"
        )
        instruction = (
            f"You are {role} drafting a {alert_type} preparedness message for the "
            "scenario context. Keep translations faithful and concise. Do NOT "
            "invent evacuation orders; instruct people to follow local authorities. "
            "Generate the message in English, Hindi (Devanagari) and Telugu. "
            "Return full JSON."
        )
        schema = json.dumps(
            {
                "title": "string",
                "summary": "string",
                "languages": [
                    {
                        "language": "en|hi|te",
                        "language_name": "English|Hindi|Telugu",
                        "title": "string",
                        "body": "string",
                    }
                ],
            }
        )
        data = self._gen(instruction, schema, temperature=0.5)
        # Guarantee the three languages exist even if the model skips one.
        langs = data.get("languages") or []
        by_code = {l.get("language"): l for l in langs if isinstance(l, dict)}
        ordered = []
        for code, name in (("en", "English"), ("hi", "Hindi"), ("te", "Telugu")):
            entry = by_code.get(code)
            if entry:
                ordered.append(
                    {
                        "language": code,
                        "language_name": name,
                        "title": entry.get("title", ""),
                        "body": entry.get("body", ""),
                    }
                )
        data["languages"] = ordered
        data["alert_type"] = alert_type
        return data

    def state_brief(self, context: dict[str, Any]) -> dict[str, Any]:
        self._context = context
        instruction = (
            "You are a state emergency-management briefing writer. Using the "
            "structured risk-engine output, produce a state-level emergency brief. "
            "Return full JSON."
        )
        schema = json.dumps(
            {
                "affectedDistricts": ["string"],
                "highRiskZones": ["string"],
                "criticalInfrastructure": {"counts": "object"},
                "hospitalsAtRisk": ["string"],
                "sheltersAtRisk": ["string"],
                "accessibilityIssues": ["string"],
                "recommendedPriorities": ["string"],
                "communicationMessage": "string",
            }
        )
        return self._gen(instruction, schema)