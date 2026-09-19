"""Read access to pipeline output files (processed/analysis parquet+csv).

Never fabricates data: if a required file is missing, raises DataNotFoundError
with a clear message telling the caller which pipeline script to run.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.config import DATA_ANALYSIS_DIR, DATA_PROCESSED_DIR


class DataNotFoundError(RuntimeError):
    pass


def _read(path: Path, hint: str) -> pd.DataFrame:
    if not path.exists():
        raise DataNotFoundError(
            f"[BLOCKED] Required data file not found: {path}. "
            f"Action: run `{hint}` after setting LAW_API_OC in .env."
        )
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_csv(path)


def load_processed_precedents() -> pd.DataFrame:
    path = DATA_PROCESSED_DIR / "precedents.parquet"
    if not path.exists():
        path = DATA_PROCESSED_DIR / "precedents.csv"
    return _read(path, "python scripts/collect_precedents.py && python scripts/normalize_precedents.py")


def load_monthly() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "monthly_trend.csv"
    return _read(path, "python scripts/run_analysis.py")


def load_yearly() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "yearly.csv"
    return _read(path, "python scripts/build_timeseries.py")


def load_keywords() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "keyword_monthly.csv"
    return _read(path, "python scripts/build_timeseries.py")


def load_courts() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "court_counts.csv"
    return _read(path, "python scripts/build_timeseries.py")


def load_anomalies() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "anomalies.csv"
    return _read(path, "python scripts/run_analysis.py")


def load_decomposition() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "decomposition.csv"
    return _read(path, "python scripts/run_decomposition.py")


def load_forecast() -> pd.DataFrame:
    path = DATA_ANALYSIS_DIR / "forecast.csv"
    return _read(path, "python scripts/run_forecast.py")
