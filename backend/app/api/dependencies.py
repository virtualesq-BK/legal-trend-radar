"""Shared FastAPI exception handling helper."""
from __future__ import annotations

import math

import pandas as pd
from fastapi import HTTPException

from app.infrastructure.repositories import DataNotFoundError


def safe_call(fn, *args, **kwargs):
    """Run fn and translate DataNotFoundError into a clean 503, not a 500 crash."""
    try:
        return fn(*args, **kwargs)
    except DataNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


def _json_safe(value):
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    return value


def to_records(df: pd.DataFrame) -> list[dict]:
    """Convert a DataFrame to JSON-safe records, turning NaN/Inf into None.

    Raw NaN (e.g. moving averages/YoY before enough history exists) is not
    valid JSON and crashes FastAPI's response renderer. Assigning None into a
    float column via `.where()` gets silently re-coerced back to NaN by
    pandas, so the substitution has to happen after `.to_dict()` instead.
    """
    records = df.to_dict(orient="records")
    return [{k: _json_safe(v) for k, v in record.items()} for record in records]
