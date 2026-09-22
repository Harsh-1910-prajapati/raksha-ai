"""Application configuration loaded from environment variables.

Never hardcode secrets. All credentials are read from the environment.
"""

from __future__ import annotations

import os
import re
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent


def _resolve_data_dir() -> Path:
    """Locate the data catalogue in dev and containerised deployments."""
    env_dir = os.getenv("RAKSHA_DATA_DIR", "")
    candidates = [
        Path(env_dir) if env_dir else None,
        Path(__file__).resolve().parent.parent.parent / "data",  # repo root data/ (dev)
        Path(__file__).resolve().parent.parent / "data",          # /app/data (Docker)
        Path(__file__).resolve().parent.parent.parent / "data",   # fallback
    ]
    for candidate in candidates:
        if candidate is None:
            continue
        if candidate.is_dir():
            return candidate
    return Path(__file__).resolve().parent.parent.parent / "data"


DATA_DIR = _resolve_data_dir()

load_dotenv(BASE_DIR / ".env")


class Settings:
    def __init__(self) -> None:
        # Gemini
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

        # Google Maps (client-side; proxying optional)
        self.google_maps_api_key: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

        # Google Earth Engine
        self.google_cloud_project: str = os.getenv("GOOGLE_CLOUD_PROJECT", "")
        self.earth_engine_project: str = os.getenv("EARTH_ENGINE_PROJECT", "")
        self.earth_engine_account: str = os.getenv("EARTH_ENGINE_SERVICE_ACCOUNT", "")
        self.earth_engine_enabled: bool = self._flag("EARTH_ENGINE_ENABLED", False)

        # Firebase (optional repository backend)
        self.firebase_project_id: str = os.getenv("FIREBASE_PROJECT_ID", "")

        # Risk engine weights (configurable, documented as prototype)
        self.risk_flood_weight: float = self._float("RISK_FLOOD_WEIGHT", 0.30)
        self.risk_wind_weight: float = self._float("RISK_WIND_WEIGHT", 0.25)
        self.risk_population_weight: float = self._float("RISK_POPULATION_WEIGHT", 0.20)
        self.risk_infrastructure_weight: float = self._float("RISK_INFRASTRUCTURE_WEIGHT", 0.15)
        self.risk_accessibility_weight: float = self._float("RISK_ACCESSIBILITY_WEIGHT", 0.10)

        # CORS (wildcards like https://*.vercel.app are compiled to a regex)
        self.cors_origins: list[str] = self._csv(
            "CORS_ORIGINS",
            "http://localhost:3000,http://127.0.0.1:3000,https://raksha-ai.vercel.app,https://*.vercel.app",
        )

        # General
        self.app_name: str = "RakshaAI"
        self.environment: str = os.getenv("ENVIRONMENT", "development")

    @staticmethod
    def _float(name: str, default: float) -> float:
        try:
            return float(os.getenv(name, default))
        except (TypeError, ValueError):
            return default

    @staticmethod
    def _flag(name: str, default: bool) -> bool:
        value = os.getenv(name)
        if value is None:
            return default
        return value.strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _csv(name: str, default: str) -> list[str]:
        raw = os.getenv(name, default)
        return [part.strip() for part in raw.split(",") if part.strip()]

    @property
    def cors_exact_origins(self) -> list[str]:
        return [origin for origin in self.cors_origins if "*" not in origin]

    @property
    def cors_origin_regex(self) -> str | None:
        patterns = [origin for origin in self.cors_origins if "*" in origin]
        if not patterns:
            return None
        parts = [re.escape(pattern).replace(r"\*", ".*") for pattern in patterns]
        return "^(" + "|".join(parts) + ")$"

    @property
    def risk_weights(self) -> dict:
        """Current risk-engine weights summary."""
        return {
            "flood": self.risk_flood_weight,
            "wind": self.risk_wind_weight,
            "population": self.risk_population_weight,
            "infrastructure": self.risk_infrastructure_weight,
            "accessibility": self.risk_accessibility_weight,
        }


@lru_cache
def get_settings() -> Settings:
    return Settings()