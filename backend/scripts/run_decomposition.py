#!/usr/bin/env python
"""Run STL decomposition on the monthly series and save results + figure."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, FIGURES_DIR  # noqa: E402
from app.services.decomposition_service import (  # noqa: E402
    InsufficientDataError,
    plot_decomposition,
    run_stl,
)


def main() -> int:
    monthly_path = DATA_ANALYSIS_DIR / "monthly.csv"
    if not monthly_path.exists():
        print("[BLOCKED] backend/data/analysis/monthly.csv not found. Run build_timeseries.py first.")
        return 2
    monthly = pd.read_csv(monthly_path)

    try:
        decomp = run_stl(monthly)
    except InsufficientDataError as exc:
        print(f"[BLOCKED] {exc} Action: collect more months of data (need >= 24 months).")
        return 2

    decomp.to_csv(DATA_ANALYSIS_DIR / "decomposition.csv", index=False)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_decomposition(decomp, str(FIGURES_DIR / "decomposition.png"))
    print(f"STL decomposition written ({len(decomp)} rows) and figure saved to {FIGURES_DIR}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
