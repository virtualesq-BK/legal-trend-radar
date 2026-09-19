from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import safe_call
from app.config import settings
from app.infrastructure.repositories import load_processed_precedents

router = APIRouter()


@router.get("/api/v1/precedents/summary")
def summary():
    df = safe_call(load_processed_precedents)
    dates = df["decision_date"].dropna() if "decision_date" in df else []
    collected_at = df["collected_at"].max() if "collected_at" in df and len(df) else None
    total = len(df)
    return {
        "total_records": total,
        "date_range_start": str(min(dates)) if len(dates) else None,
        "date_range_end": str(max(dates)) if len(dates) else None,
        "keywords": sorted(df["search_keyword"].dropna().unique().tolist()) if "search_keyword" in df else [],
        "courts": sorted(df["court_type"].dropna().unique().tolist()) if "court_type" in df else [],
        "data_collected_at": str(collected_at) if collected_at is not None else None,
        "min_required": settings.min_records_required,
        "sufficient": total >= settings.min_records_required,
    }
