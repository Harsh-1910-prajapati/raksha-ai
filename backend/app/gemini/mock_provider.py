"""Deterministic mock AI provider.

Produces structured decision-support text built directly from the risk-engine
output. It never pretends to be a live model — the ai_provider field is set to
'mock' and the UI shows a DEMO/MOCK label.
"""

from __future__ import annotations

from typing import Any

from app.gemini.provider import GeminiProvider

EN = {
    "alert_title": "CYCLONE PREPAREDNESS ALERT",
    "flood_alert_title": "FLOOD PREPAREDNESS ALERT",
    "rain_alert_title": "EXTREME RAINFALL ALERT",
}
HI = {
    "alert_title_c": "चक्रवात तैयारी अलर्ट",
    "alert_title_f": "बाढ़ तैयारी अलर्ट",
    "alert_title_r": "अत्यधिक वर्षा अलर्ट",
}
TE = {
    "alert_title_c": "తుఫాను సన్నద్ధత హెచ్చరిక",
    "alert_title_f": "వరద సన్నద్ధత హెచ్చరిక",
    "alert_title_r": "అతివృష్టి హెచ్చరిక",
}

_TRANSLATIONS_FRIENDLY = {
    "hi": "चक्रवात स्थिति के अनुसार निम्नलिखित सावधानियाँ बरतें।",
    "te": "తుఫాను పరిస్థితిని దృష్టిలో ఉంచుకుని కింది జాగ్రత్తలు తీసుకోండి.",
}
_TRANSLATIONS_FOLLOW = {
    "hi": "अधिकारियों के निर्देशों का पालन करें। जल-भरे रास्तों से यात्रा न करें।",
    "te": "స్థానిక అధికారుల ఆదేశాలను పాటించండి. వరదలో మునిగిన రోడ్ల గుండా ప్రయాణించవద్దు.",
}


class MockGeminiProvider(GeminiProvider):
    name = "mock"
    note = (
        "Mock AI provider active (no GEMINI_API_KEY configured). Responses are "
        "generated deterministically from risk-engine values."
    )

    # -- analyze -------------------------------------------------------------

    def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        overall = context["overallRisk"]
        level = context["riskLevel"]
        loc = context["location"]
        disaster = context["disasterName"]

        summary = (
            f"{disaster} scenario for {loc}: the RakshaAI prototype risk engine "
            f"estimates {overall:.0f}/100 ({level}) overall risk within an "
            f"{context['impactRadius']:.0f} km radius. Wind speeds of "
            f"{context['windSpeed']:.0f} km/h and rainfall of "
            f"{context['rainfall']:.0f} mm are projected, combined with "
            f"{context['stormSurge']:.1f} m of storm surge. "
            f"Approximately {self._fmt_pop(context['populationExposed'])} people "
            "may be exposed. Pre-positioning and early public communication are "
            "recommended before conditions deteriorate."
        )

        priority_areas = [
            f"{a['label']} (~{a['riskScore']:.0f}/100, {a['riskLevel']}) — "
            + "; ".join(a.get("factors", [])[:3])
            for a in (context.get("highRiskAreas") or [])[:4]
        ]
        if not priority_areas:
            priority_areas = ["No sector crossed the HIGH threshold; keep monitoring."]

        infra = context.get("criticalInfrastructure") or []
        infra_risks = [
            f"{i['name']} ({i['type']}) — {i['level']} risk ({i['risk']:.0f}); threats: "
            + ", ".join(i.get("threats", []))
            for i in infra[:5]
        ] or ["No high-risk assets identified in this run."]

        recommended = [
            f"Pre-position emergency supplies near the highest-risk hospitals in {context['district']}.",
            "Inspect access roads and alternate routes to cyclone shelters.",
            "Verify backup power at hospitals, water plants and telecom towers.",
            "Review evacuation routes in coastal and low-lying sectors.",
            "Brief local administration and issue multilingual preparedness guidance.",
        ]

        return {
            "ai_provider": self.name,
            "provider_note": self.note,
            "summary": summary,
            "priorityAreas": priority_areas,
            "infrastructureRisks": infra_risks,
            "recommendedActions": recommended,
            "resourcePriorities": [
                "Boats, pumps and rescue teams near low-elevation sectors.",
                "Mobile generators for district hospital and power substation.",
                "Drinking water and hygiene kits for shelter capacity.",
                "Communication spares (satellite phones) if network fails.",
            ],
            "evacuationConsiderations": [
                "Prioritise coastal and surge-exposed sectors first.",
                "Shelter-dependent populations need transport support.",
                "Activate last-mile warning through local panchayat networks.",
                "Do not instruct citizens beyond official guidance.",
            ],
            "communicationGuidance": [
                "Publish alerts in English, Hindi and local language (Telugu/Odia/Bengali/Tamil/Gujarati).",
                "Share bulletins over radio, SMS and public-address systems.",
                "Keep messages short, practical and consistent with SDMA guidance.",
            ],
        }

    # -- action plan ---------------------------------------------------------

    def action_plan(self, context: dict[str, Any]) -> dict[str, Any]:
        level = context["riskLevel"]
        return {
            "ai_provider": self.name,
            "provider_note": self.note,
            "immediateActions": [
                "Activate district control room and incident-response team.",
                "Confirm shelter readiness and stock basics (water, food, lights).",
                "Check backup power and generators at hospitals and power assets.",
            ],
            "beforeImpact": [
                "Pre-position supplies and rescue boats in high-risk sectors.",
                "Clear drainage and culverts on risk-level roads.",
                "Relocate medical teams/supplies toward exposed hospitals.",
                "Identify alternate access routes for each critical facility.",
            ],
            "duringEvent": [
                "Restrict travel on flooded and high-risk roads.",
                "Monitor water levels and infrastructure status hourly.",
                "Keep public informed via short multilingual updates.",
            ],
            "recovery": [
                "Rapid damage assessment of roads, power and water lines.",
                "Restore drinking water and sanitation first.",
                "Debrief and update risk models with observed impacts.",
            ],
        }

    # -- alert ---------------------------------------------------------------

    def alert(self, context: dict[str, Any], alert_type: str) -> dict[str, Any]:
        disaster_key = context["disaster"]
        disaster = context["disasterName"]
        loc = context["location"]
        wind = context["windSpeed"]
        rain = context["rainfall"]

        if alert_type == "authority":
            title = "Authority Briefing — " + disaster + " scenario, " + loc
            summary = f"{title}. Risk index {context['overallRisk']:.0f}/100 ({context['riskLevel']})."
        else:
            title_key = {
                "CYCLONE": "alert_title",
                "FLOOD": "flood_alert_title",
                "EXTREME_RAINFALL": "rain_alert_title",
            }.get(disaster_key, "alert_title")
            title = EN[title_key]
            summary = (
                f"{disaster} conditions are projected for {loc}. Expected wind "
                f"around {wind:.0f} km/h and rainfall of about {rain:.0f} mm. "
            )

        body_en = (
            f"{summary} Residents in high-risk zones should follow local authority "
            "instructions and prepare essential supplies. Do not travel through "
            "flooded roads. Stay tuned to official broadcasts."
        )

        langs = [
            {
                "language": "en",
                "language_name": "English",
                "title": title,
                "body": body_en,
            },
            {
                "language": "hi",
                "language_name": "Hindi",
                "title": self._hi_title(disaster_key),
                "body": (
                    f"{loc} के लिए {disaster} संभावित है। "
                    + _TRANSLATIONS_FRIENDLY["hi"]
                    + " "
                    + _TRANSLATIONS_FOLLOW["hi"]
                ),
            },
            {
                "language": "te",
                "language_name": "Telugu",
                "title": self._te_title(disaster_key),
                "body": (
                    f"{loc}కి {disaster} పరిస్థితి అంచనా వేయబడింది. "
                    + _TRANSLATIONS_FRIENDLY["te"]
                    + " "
                    + _TRANSLATIONS_FOLLOW["te"]
                ),
            },
        ]
        return {
            "ai_provider": self.name,
            "provider_note": self.note,
            "alert_type": alert_type,
            "title": title,
            "summary": summary,
            "languages": langs,
        }

    # -- state brief -----------------------------------------------------------

    def state_brief(self, context: dict[str, Any]) -> dict[str, Any]:
        state = context["state"]
        districts = [context["district"]]
        zones = [a["label"] for a in (context.get("highRiskAreas") or [])[:5]]
        infra = context.get("criticalInfrastructure") or []
        hospitals = [i["name"] for i in infra if i["type"] == "hospital"][:3]
        shelters = [i["name"] for i in infra if i["type"] == "shelter"][:3]

        return {
            "ai_provider": self.name,
            "provider_note": self.note,
            "state": state,
            "generatedAt": "",
            "affectedDistricts": districts,
            "highRiskZones": zones,
            "criticalInfrastructure": {
                "hospitals": sum(1 for i in infra if i["type"] == "hospital"),
                "shelters": sum(1 for i in infra if i["type"] == "shelter"),
                "power": sum(1 for i in infra if i["type"] == "power"),
                "roads": sum(1 for i in infra if i["type"] in {"road", "bridge"}),
            },
            "hospitalsAtRisk": hospitals,
            "sheltersAtRisk": shelters,
            "accessibilityIssues": context.get("accessibilityIssues") or [],
            "recommendedPriorities": [
                "Pre-position teams in sectors flagged HIGH/CRITICAL.",
                "Secure power and water continuity for medical facilities.",
                "Keep shelter routes clear and communicated.",
                "Activate multilingual alerting for affected districts.",
            ],
            "communicationMessage": (
                f"State response control room should monitor {state} scenario for "
                f"{context['district']} and co-ordinate district collectors on "
                "pre-positioning and public alerting."
            ),
        }

    # -- helpers --------------------------------------------------------------

    @staticmethod
    def _fmt_pop(n: int) -> str:
        if n >= 1_000_000:
            return f"{n / 1_000_000:.1f} million"
        if n >= 1_000:
            return f"{n / 1_000:.0f} thousand"
        return str(n)

    @staticmethod
    def _hi_title(key: str) -> str:
        return {
            "CYCLONE": HI["alert_title_c"],
            "FLOOD": HI["alert_title_f"],
            "EXTREME_RAINFALL": HI["alert_title_r"],
        }.get(key, HI["alert_title_c"])

    @staticmethod
    def _te_title(key: str) -> str:
        return {
            "CYCLONE": TE["alert_title_c"],
            "FLOOD": TE["alert_title_f"],
            "EXTREME_RAINFALL": TE["alert_title_r"],
        }.get(key, TE["alert_title_c"])