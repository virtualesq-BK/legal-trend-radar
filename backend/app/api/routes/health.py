from __future__ import annotations

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/health")
def health():
    return {
        "status": "ok",
        "law_api_configured": bool(settings.law_api_oc),
        "openai_configured": bool(settings.openai_api_key),
    }
