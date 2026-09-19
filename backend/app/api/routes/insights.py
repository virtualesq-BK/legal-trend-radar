from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.config import settings
from app.infrastructure.repositories import DataNotFoundError, load_monthly
from app.services.llm_service import generate_insights

router = APIRouter()


@router.get("/api/v1/insights")
def insights():
    try:
        monthly = load_monthly()
    except DataNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    stats = {
        "total_months": len(monthly),
        "total_count": int(monthly["count"].sum()) if "count" in monthly else 0,
        "latest_period": monthly["period"].iloc[-1] if len(monthly) else None,
        "latest_yoy_pct_change": (
            float(monthly["yoy_pct_change"].iloc[-1])
            if "yoy_pct_change" in monthly and len(monthly)
            else None
        ),
        "mean_count": float(monthly["count"].mean()) if "count" in monthly and len(monthly) else None,
        "max_count": float(monthly["count"].max()) if "count" in monthly and len(monthly) else None,
        "min_count": float(monthly["count"].min()) if "count" in monthly and len(monthly) else None,
    }
    return generate_insights(stats)


@router.get("/api/v1/metadata")
def metadata():
    return {
        "data_source": "국가법령정보센터 (law.go.kr) Open API",
        "default_keywords": settings.default_keywords,
        "default_start_date": settings.default_start_date,
        "default_end_date": settings.default_end_date,
        "forecast_horizon": settings.forecast_horizon,
        "disclaimer": (
            "This service provides statistical/time-series analysis of public precedent "
            "search-result counts. It is NOT legal advice and does not predict litigation outcomes."
        ),
    }


@router.post("/api/v1/collect")
def trigger_collect():
    if not settings.law_api_oc:
        raise HTTPException(
            status_code=503,
            detail=(
                "[BLOCKED] LAW_API_OC is not set. Cannot trigger collection. "
                "Set LAW_API_OC in .env, then run backend/scripts/collect_precedents.py."
            ),
        )
    raise HTTPException(
        status_code=501,
        detail=(
            "Synchronous collection via API is not implemented to avoid long-running "
            "HTTP requests. Run `python backend/scripts/collect_precedents.py` from the CLI "
            "(see Makefile target `collect`)."
        ),
    )
