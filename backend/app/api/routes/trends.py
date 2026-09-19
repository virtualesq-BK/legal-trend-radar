from __future__ import annotations

from fastapi import APIRouter

from app.api.dependencies import safe_call, to_records
from app.infrastructure.repositories import load_courts, load_keywords, load_monthly, load_yearly

router = APIRouter()


@router.get("/api/v1/trends/monthly")
def monthly():
    df = safe_call(load_monthly)
    return to_records(df)


@router.get("/api/v1/trends/yearly")
def yearly():
    df = safe_call(load_yearly)
    return to_records(df)


@router.get("/api/v1/trends/keywords")
def keywords():
    df = safe_call(load_keywords)
    return to_records(df)


@router.get("/api/v1/trends/courts")
def courts():
    df = safe_call(load_courts)
    return to_records(df)
