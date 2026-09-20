"""Download the monthly trend table as CSV or JSON (real data, no transformation)."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.dependencies import safe_call, to_records
from app.infrastructure.repositories import load_monthly

router = APIRouter()


@router.get("/api/v1/export/monthly")
def export_monthly(format: str = Query("csv", pattern="^(csv|json)$")):
    df = safe_call(load_monthly)
    if format == "csv":
        return PlainTextResponse(
            df.to_csv(index=False),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=legal_trend_radar_monthly.csv"},
        )
    if format == "json":
        return JSONResponse(
            to_records(df),
            headers={"Content-Disposition": "attachment; filename=legal_trend_radar_monthly.json"},
        )
    raise HTTPException(status_code=400, detail="format must be 'csv' or 'json'")
