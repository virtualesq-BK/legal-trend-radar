"""Build monthly/yearly/keyword/court aggregations from normalized precedent records."""
from __future__ import annotations

import pandas as pd


def monthly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return a DataFrame indexed by month (period='YYYY-MM') with a `count` column.

    Fills gaps with zero counts so downstream time-series methods see a
    continuous monthly index.
    """
    d = df.dropna(subset=["decision_date"]).copy()
    d["decision_date"] = pd.to_datetime(d["decision_date"])
    d["period"] = d["decision_date"].dt.to_period("M")
    counts = d.groupby("period").size().rename("count")
    if counts.empty:
        return pd.DataFrame(columns=["period", "count"])
    full_index = pd.period_range(counts.index.min(), counts.index.max(), freq="M")
    counts = counts.reindex(full_index, fill_value=0)
    out = counts.rename_axis("period").reset_index()
    out["period"] = out["period"].astype(str)
    return out


def yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna(subset=["decision_date"]).copy()
    d["decision_date"] = pd.to_datetime(d["decision_date"])
    d["year"] = d["decision_date"].dt.year
    out = d.groupby("year").size().rename("count").reset_index()
    return out.sort_values("year")


def keyword_monthly_counts(df: pd.DataFrame) -> pd.DataFrame:
    d = df.dropna(subset=["decision_date"]).copy()
    d["decision_date"] = pd.to_datetime(d["decision_date"])
    d["period"] = d["decision_date"].dt.to_period("M").astype(str)
    out = d.groupby(["period", "search_keyword"]).size().rename("count").reset_index()
    return out.sort_values(["period", "search_keyword"])


def court_counts(df: pd.DataFrame) -> pd.DataFrame:
    out = df.groupby("court_type").size().rename("count").reset_index()
    return out.sort_values("count", ascending=False)
