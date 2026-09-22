"""Infrastructure exposure scoring based on at-risk asset counts and severity."""

from __future__ import annotations

from app.utils.geo import clamp, mean


def infrastructure_exposure(
    items: list[dict],
    weight_by_type: dict[str, float] | None = None,
) -> tuple[float, list[str]]:
    weight_by_type = weight_by_type or {
        "hospital": 1.5,
        "power": 1.4,
        "water": 1.3,
        "bridge": 1.2,
        "shelter": 1.1,
        "fire": 1.0,
        "police": 1.0,
        "school": 0.9,
        "road": 0.8,
    }

    if not items:
        return 0.0, ["No infrastructure assets within the impact area"]

    weighted = [item["riskScore"] * weight_by_type.get(item["type"], 1.0) for item in items]
    weight_sum = sum(weight_by_type.get(item["type"], 1.0) for item in items)
    score = clamp(sum(weighted) / weight_sum)

    names = [item["name"] for item in items[:4]]
    factors: list[str] = []
    if len(items) >= 12:
        factors.append(f"Dense infrastructure presence ({len(items)} assets in radius)")
    elif len(items) >= 6:
        factors.append(f"Multiple exposed assets ({len(items)} in radius)")
    critical = [item for item in items if item["riskLevel"] in {"HIGH", "CRITICAL"}][:5]
    if critical:
        factors.append(
            "High/critical risk assets: " + ", ".join(item.get("name", item["type"]) for item in critical)
        )
    return round(score, 1), factors