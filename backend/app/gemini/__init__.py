"""Gemini provider factory.

If GEMINI_API_KEY is set, the live provider is used. Otherwise (or when the
live call fails), the mock provider keeps the product fully runnable.
"""

from __future__ import annotations

from app.config import get_settings
from app.gemini.mock_provider import MockGeminiProvider
from app.gemini.provider_gemini import GeminiProviderImpl


def get_gemini_provider(force_mock: bool = False):
    settings = get_settings()
    if settings.gemini_api_key and not force_mock:
        provider = GeminiProviderImpl()
        if provider.available:
            return provider
    return MockGeminiProvider()