#!/usr/bin/env python
"""Build monthly/yearly/keyword/court aggregations from processed precedents."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, DATA_PROCESSED_DIR  # noqa: E402
from app.services.timeseries_service import (  # noqa: E402
    court_counts,
    keyword_monthly_counts,
    monthly_counts,
    yearly_counts,
)


def load_processed() -> pd.DataFrame:
    parquet = DATA_PROCESSED_DIR / "precedents.parquet"
    csv = DATA_PROCESSED_DIR / "precedents.csv"
    if parquet.exists():
        return pd.read_parquet(parquet)
    if csv.exists():
        return pd.read_csv(csv)
    raise SystemExit(
        "[BLOCKED] No processed data found. Action: run collect_precedents.py "
        "then normalize_precedents.py first."
    )


def main() -> int:
    df = load_processed()
    if "decision_date" in df:
        df["decision_date"] = pd.to_datetime(df["decision_date"], errors="coerce")

    DATA_ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    monthly_counts(df).to_csv(DATA_ANALYSIS_DIR / "monthly.csv", index=False)
    yearly_counts(df).to_csv(DATA_ANALYSIS_DIR / "yearly.csv", index=False)
    keyword_monthly_counts(df).to_csv(DATA_ANALYSIS_DIR / "keyword_monthly.csv", index=False)
    court_counts(df).to_csv(DATA_ANALYSIS_DIR / "court_counts.csv", index=False)
    print(f"Time series aggregations written to {DATA_ANALYSIS_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
