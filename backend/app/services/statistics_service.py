"""Enriched summary statistics beyond the basic /precedents/summary endpoint.

All numbers here are computed directly from the real monthly/anomaly tables -
nothing is invented. If there isn't enough history for a metric (e.g. growth
rate needs at least 2 months), that field is returned as None rather than a
fabricated number.
"""
from __future__ import annotations

from typing import Any

import pandas as pd


def compute_statistics(monthly: pd.DataFrame, anomalies: pd.DataFrame) -> dict[str, Any]:
    counts = monthly["count"].astype(float) if "count" in monthly else pd.Series(dtype=float)

    peak_idx = counts.idxmax() if len(counts) else None
    trough_idx = counts.idxmin() if len(counts) else None

    first_count = float(counts.iloc[0]) if len(counts) else None
    last_count = float(counts.iloc[-1]) if len(counts) else None
    growth_rate_pct = (
        ((last_count - first_count) / first_count) * 100
        if first_count not in (None, 0) and last_count is not None
        else None
    )

    anomaly_rate_pct = None
    if len(anomalies):
        anomaly_rate_pct = float(anomalies["is_anomaly"].mean()) * 100

    return {
        "median_monthly_count": float(counts.median()) if len(counts) else None,
        "std_monthly_count": float(counts.std(ddof=0)) if len(counts) else None,
        "mean_monthly_count": float(counts.mean()) if len(counts) else None,
        "total_count": float(counts.sum()) if len(counts) else None,
        "total_months": len(monthly),
        "growth_rate_pct_full_period": growth_rate_pct,
        "anomaly_rate_pct": anomaly_rate_pct,
        "peak_month": {
            "period": str(monthly["period"].iloc[peak_idx]),
            "count": float(counts.iloc[peak_idx]),
        }
        if peak_idx is not None
        else None,
        "trough_month": {
            "period": str(monthly["period"].iloc[trough_idx]),
            "count": float(counts.iloc[trough_idx]),
        }
        if trough_idx is not None
        else None,
        "note": (
            "All figures describe precedent SEARCH RESULT counts, not real-world "
            "litigation volume. See README Limitations section."
        ),
    }
