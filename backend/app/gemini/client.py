"""Gemini REST client.

Uses the public Models.generateContent REST endpoint so no SDK is required.
Falls back through providers when the API key is missing or the call fails.
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.config import get_settings


class GeminiClientError(Exception):
    pass


def extract_json(text: str) -> dict[str, Any]:
    """Extract the first JSON object from a model response."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise GeminiClientError("Response did not contain a JSON object")
        data = json.loads(cleaned[start : end + 1])
    if not isinstance(data, dict):
        raise GeminiClientError("JSON response was not an object")
    return data


class GeminiRESTClient:
    endpoint = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, temperature: float = 0.5) -> dict[str, Any]:
        url = self.endpoint.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 2048,
                "responseMimeType": "application/json",
            },
        }
        headers = {"Content-Type": "application/json"}
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(
                    url, params={"key": self.api_key}, headers=headers, json=payload
                )
        except httpx.HTTPError as exc:
            raise GeminiClientError(f"Gemini network error: {exc}") from exc

        if resp.status_code == 400:
            raise GeminiClientError(
                "Gemini request rejected (400). Check GEMINI_MODEL is available for your key."
            )
        if resp.status_code == 401 or resp.status_code == 403:
            raise GeminiClientError("Gemini authentication failed. Check GEMINI_API_KEY.")
        if resp.status_code != 200:
            raise GeminiClientError(f"Gemini HTTP {resp.status_code}: {resp.text[:300]}")

        try:
            data = resp.json()
        except json.JSONDecodeError as exc:
            raise GeminiClientError("Gemini returned non-JSON response") from exc
        return data

    def generate_json(self, prompt: str, temperature: float = 0.4) -> dict[str, Any]:
        raw = self.generate(prompt, temperature=temperature)
        try:
            text = raw["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiClientError("Malformed Gemini response envelope") from exc
        return extract_json(text)


def make_client() -> GeminiRESTClient | None:
    settings = get_settings()
    if not settings.gemini_api_key:
        return None
    return GeminiRESTClient(settings.gemini_api_key, settings.gemini_model)