from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import safe_call, to_records
from app.infrastructure.repositories import load_anomalies

router = APIRouter()


@router.get("/api/v1/anomalies")
def anomalies():
    df = safe_call(load_anomalies)
    return to_records(df)
