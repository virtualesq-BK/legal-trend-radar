from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import safe_call, to_records
from app.infrastructure.repositories import load_forecast

router = APIRouter()

DISCLAIMER = (
    "This forecast is a statistical extrapolation of past precedent-search counts. "
    "It is NOT a legal or litigation prediction and must not be used as legal advice."
)


@router.get("/api/v1/forecast")
def forecast():
    df = safe_call(load_forecast)
    return {"disclaimer": DISCLAIMER, "points": to_records(df)}


@router.get("/api/v1/decomposition")
def decomposition():
    from app.infrastructure.repositories import load_decomposition

    df = safe_call(load_decomposition)
    return to_records(df)
