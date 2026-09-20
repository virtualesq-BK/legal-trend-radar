from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import safe_call
from app.infrastructure.repositories import load_anomalies, load_monthly
from app.services.statistics_service import compute_statistics

router = APIRouter()


@router.get("/api/v1/data/statistics")
def statistics():
    monthly = safe_call(load_monthly)
    anomalies = safe_call(load_anomalies)
    return compute_statistics(monthly, anomalies)
