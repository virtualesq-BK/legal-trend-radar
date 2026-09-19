"""Central configuration for the Legal Trend Radar backend.

All secrets/config come from environment variables (loaded from a .env file
at the repo root via python-dotenv). Nothing here is hardcoded - see the
`.env.example` at the repo root for the full list of variables.
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo root is two levels up from backend/app/config.py -> backend/ -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "backend"
DATA_RAW_DIR = BACKEND_ROOT / "data" / "raw"
DATA_PROCESSED_DIR = BACKEND_ROOT / "data" / "processed"
DATA_ANALYSIS_DIR = BACKEND_ROOT / "data" / "analysis"
REPORTS_DIR = REPO_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Load .env from repo root (harmless if absent)
load_dotenv(REPO_ROOT / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(REPO_ROOT / ".env"), extra="ignore")

    # Accepts either LAW_API_OC (documented name) or LAW_OC (alternate name
    # this project's .env happens to use) - whichever is set wins.
    law_api_oc: str = Field(
        default="", validation_alias=AliasChoices("LAW_API_OC", "LAW_OC")
    )
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_base_url: str = ""
    backend_url: str = "http://localhost:8000"
    next_public_api_url: str = "http://localhost:8000"
    default_start_date: str = "2016-01-01"
    default_end_date: str = "2026-12-31"
    forecast_horizon: int = 6
    run_integration_tests: bool = False

    law_api_base: str = "http://www.law.go.kr/DRF"
    default_keywords: list[str] = [
        "계약",
        "계약해제",
        "계약해지",
        "손해배상",
        "위약금",
        "채무불이행",
    ]
    min_records_required: int = 100


settings = Settings()


def require_law_api_key() -> str:
    """Return the configured LAW_API_OC or raise a clear, actionable error.

    This function is the single choke point that enforces the "never fall
    back to fake data" rule for anything that talks to law.go.kr.
    """
    if not settings.law_api_oc:
        raise RuntimeError(
            "[BLOCKED] LAW_API_OC is not set. "
            "Real precedent data cannot be collected from law.go.kr without it. "
            "Fix: obtain an OC id from https://open.law.go.kr (사용자 인증키) and "
            "set LAW_API_OC=<your-oc-id> in the repo-root .env file (see .env.example)."
        )
    return settings.law_api_oc
