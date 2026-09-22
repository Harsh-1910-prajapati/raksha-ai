"""Risk level classification.

Classes mirror the requested bands:
  0-25  LOW, 26-50 MODERATE, 51-75 HIGH, 76-100 CRITICAL
"""

from __future__ import annotations

THRESHOLDS = [("CRITICAL", 76), ("HIGH", 51), ("MODERATE", 26), ("LOW", 0)]


def classify(score: float) -> str:
    for level, minimum in THRESHOLDS:
        if score >= minimum:
            return level
    return "LOW"


def severity_class(score: float) -> str:
    return classify(score).lower()