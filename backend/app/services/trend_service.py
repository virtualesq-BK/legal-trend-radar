"""Moving averages, YoY change, and rolling volatility for a monthly count series."""
from __future__ import annotations

import pandas as pd


def add_moving_averages(monthly: pd.DataFrame) -> pd.DataFrame:
    out = monthly.copy()
    out["ma_3m"] = out["count"].rolling(window=3, min_periods=1).mean()
    out["ma_12m"] = out["count"].rolling(window=12, min_periods=1).mean()
    return out


def add_yoy_change(monthly: pd.DataFrame) -> pd.DataFrame:
    out = monthly.copy()
    out["yoy_pct_change"] = out["count"].pct_change(periods=12) * 100
    return out


def add_volatility(monthly: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    out = monthly.copy()
    out["volatility"] = out["count"].rolling(window=window, min_periods=1).std()
    return out


def build_trend_table(monthly: pd.DataFrame) -> pd.DataFrame:
    out = add_moving_averages(monthly)
    out = add_yoy_change(out)
    out = add_volatility(out)
    return out
