#!/usr/bin/env python
"""Push the current analysis output to Firestore's `data` collection.

Run this after the analysis pipeline (run_analysis.py, run_decomposition.py,
run_forecast.py) to persist a timestamped snapshot of real results. Requires
FIREBASE_CREDENTIALS_JSON in .env; if it isn't set, this prints a clear
[BLOCKED] message and exits non-zero rather than silently doing nothing.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, DATA_PROCESSED_DIR  # noqa: E402
from app.services.firestore_service import save_analysis_snapshot  # noqa: E402
from app.services.statistics_service import compute_statistics  # noqa: E402


def _read_csv(name: str) -> pd.DataFrame | None:
    path = DATA_ANALYSIS_DIR / name
    return pd.read_csv(path) if path.exists() else None


def main() -> int:
    monthly = _read_csv("monthly_trend.csv")
    if monthly is None:
        monthly = _read_csv("monthly.csv")
    if monthly is None:
        print("[BLOCKED] No analysis output found. Run build_timeseries.py and run_analysis.py first.")
        return 2

    yearly = _read_csv("yearly.csv")
    anomalies = _read_csv("anomalies.csv")
    forecast_metrics = _read_csv("forecast_metrics.csv")

    processed_path = DATA_PROCESSED_DIR / "precedents.csv"
    collected_at = None
    total_records = len(monthly["count"]) if "count" in monthly else None
    if processed_path.exists():
        processed = pd.read_csv(processed_path)
        total_records = len(processed)
        if "collected_at" in processed and len(processed):
            collected_at = str(processed["collected_at"].max())

    snapshot = {
        "collected_at": collected_at,
        "total_records": total_records,
        "monthly_trend": monthly.to_dict(orient="records"),
        "yearly_trend": yearly.to_dict(orient="records") if yearly is not None else [],
        "statistics": compute_statistics(monthly, anomalies if anomalies is not None else pd.DataFrame({"is_anomaly": []})),
        "forecast_metrics": forecast_metrics.to_dict(orient="records") if forecast_metrics is not None else [],
    }

    result = save_analysis_snapshot(snapshot)
    if not result["saved"]:
        print(result["reason"])
        return 2

    print(f"Saved analysis snapshot to Firestore `data` collection, doc id: {result['doc_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
