"""Pydantic response/request schemas used by the FastAPI layer."""
from __future__ import annotations

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str
    action_required: str | None = None


class SummaryResponse(BaseModel):
    total_records: int
    date_range_start: str | None
    date_range_end: str | None
    keywords: list[str]
    courts: list[str]
    data_collected_at: str | None
    min_required: int
    sufficient: bool


class MonthlyPoint(BaseModel):
    period: str
    count: int
    ma_3m: float | None = None
    ma_12m: float | None = None
    yoy_pct_change: float | None = None
    volatility: float | None = None


class YearlyPoint(BaseModel):
    year: int
    count: int


class KeywordSeriesPoint(BaseModel):
    period: str
    keyword: str
    count: int


class CourtSeriesPoint(BaseModel):
    court_type: str
    count: int


class AnomalyPoint(BaseModel):
    period: str
    count: int
    method: str
    threshold: float
    score: float
    is_anomaly: bool


class DecompositionResponse(BaseModel):
    period: list[str]
    observed: list[float]
    trend: list[float | None]
    seasonal: list[float | None]
    resid: list[float | None]


class ForecastPoint(BaseModel):
    date: str
    actual: float | None
    forecast: float | None
    lower_ci: float | None
    upper_ci: float | None
    model: str


class ForecastResponse(BaseModel):
    best_model: str
    metrics: dict[str, dict[str, float]]
    points: list[ForecastPoint]
    disclaimer: str = (
        "This forecast is a statistical extrapolation of past precedent counts. "
        "It is NOT a legal or litigation prediction and must not be used as legal advice."
    )


class InsightsResponse(BaseModel):
    available: bool
    summary: str
    observations: list[str] = []
    interpretations: list[str] = []
    hypotheses: list[str] = []
    limitations: list[str] = []
    reason: str | None = None
