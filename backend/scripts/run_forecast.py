#!/usr/bin/env python
"""Compare Naive/MovingAverage/ARIMA/SARIMA and forecast FORECAST_HORIZON months ahead.

Chronological train/validation split (no random shuffling). Wrapped
defensively so a model-fitting failure never crashes the pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, FIGURES_DIR, settings  # noqa: E402
from app.services.forecast_service import evaluate_models, forecast_future, pick_best  # noqa: E402


def plot_forecast(monthly: pd.DataFrame, future_periods, future_mean, lower, upper, out_path: str) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly["period"], monthly["count"], label="Observed")
    ax.plot(future_periods, future_mean, label="Forecast", linestyle="--")
    if lower is not None and upper is not None:
        ax.fill_between(future_periods, lower, upper, alpha=0.2, label="95% CI")
    ax.legend()
    ax.set_title("Precedent Count Forecast (statistical extrapolation, not legal prediction)")
    plt.xticks(rotation=90)
    plt.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main() -> int:
    monthly_path = DATA_ANALYSIS_DIR / "monthly.csv"
    if not monthly_path.exists():
        print("[BLOCKED] backend/data/analysis/monthly.csv not found. Run build_timeseries.py first.")
        return 2
    monthly = pd.read_csv(monthly_path)
    series = monthly["count"].astype(float)

    results = evaluate_models(series)
    if not results:
        print("[BLOCKED] Not enough data to evaluate any forecasting model (need >= 6 months).")
        return 2

    best = pick_best(results)
    horizon = settings.forecast_horizon
    future_mean, lower, upper = forecast_future(series, best, horizon)

    last_period = pd.Period(monthly["period"].iloc[-1], freq="M")
    future_periods = [str(last_period + i) for i in range(1, horizon + 1)]

    rows = []
    for i, p in enumerate(monthly["period"]):
        rows.append(
            {
                "date": p,
                "actual": float(monthly["count"].iloc[i]),
                "forecast": None,
                "lower_ci": None,
                "upper_ci": None,
                "model": "observed",
            }
        )
    for i, p in enumerate(future_periods):
        rows.append(
            {
                "date": p,
                "actual": None,
                "forecast": float(future_mean.iloc[i]),
                "lower_ci": float(lower.iloc[i]) if lower is not None else None,
                "upper_ci": float(upper.iloc[i]) if upper is not None else None,
                "model": best,
            }
        )
    out_df = pd.DataFrame(rows)
    out_df.to_csv(DATA_ANALYSIS_DIR / "forecast.csv", index=False)

    metrics = {
        name: {"mae": r.mae, "rmse": r.rmse, **({"mape": r.mape} if r.mape is not None else {})}
        for name, r in results.items()
    }
    pd.DataFrame(metrics).to_csv(DATA_ANALYSIS_DIR / "forecast_metrics.csv")

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    plot_forecast(monthly, future_periods, future_mean, lower, upper, str(FIGURES_DIR / "forecast.png"))

    print(f"Best model: {best}. Metrics: {metrics}")
    print(f"Forecast written to {DATA_ANALYSIS_DIR / 'forecast.csv'}, figure to {FIGURES_DIR / 'forecast.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
