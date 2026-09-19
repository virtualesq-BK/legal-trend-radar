"""Anomaly detection on the monthly precedent-count series.

Two independent methods are provided; each row records the method,
threshold, computed score and whether it was flagged as anomalous.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def detect_zscore(monthly: pd.DataFrame, threshold: float = 2.0) -> pd.DataFrame:
    out = monthly.copy()
    series = out["count"].astype(float)
    mu = series.mean()
    sigma = series.std(ddof=0)
    if sigma == 0 or np.isnan(sigma):
        score = pd.Series(0.0, index=series.index)
    else:
        score = (series - mu) / sigma
    out["method"] = "zscore"
    out["threshold"] = threshold
    out["score"] = score
    out["is_anomaly"] = score.abs() > threshold
    return out


def detect_iqr(monthly: pd.DataFrame, k: float = 1.5) -> pd.DataFrame:
    out = monthly.copy()
    series = out["count"].astype(float)
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    lower, upper = q1 - k * iqr, q3 + k * iqr
    out["method"] = "iqr"
    out["threshold"] = k
    # score: distance from nearest bound, 0 if inside range
    dist_low = (lower - series).clip(lower=0)
    dist_high = (series - upper).clip(lower=0)
    out["score"] = dist_low + dist_high
    out["is_anomaly"] = (series < lower) | (series > upper)
    return out


def combined_anomalies(monthly: pd.DataFrame) -> pd.DataFrame:
    z = detect_zscore(monthly)[["period", "count", "method", "threshold", "score", "is_anomaly"]]
    iqr = detect_iqr(monthly)[["period", "count", "method", "threshold", "score", "is_anomaly"]]
    return pd.concat([z, iqr], ignore_index=True)
