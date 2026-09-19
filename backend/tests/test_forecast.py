from __future__ import annotations

import pandas as pd

from app.services.forecast_service import (
    chronological_split,
    evaluate_models,
    forecast_future,
    pick_best,
)


def test_chronological_split_no_shuffle():
    series = pd.Series(range(20))
    train, val = chronological_split(series, val_ratio=0.2)
    assert len(train) == 16
    assert len(val) == 4
    assert list(train) == list(range(16))
    assert list(val) == list(range(16, 20))


def test_evaluate_models_returns_metrics(synthetic_monthly_df):
    series = synthetic_monthly_df["count"].astype(float)
    results = evaluate_models(series)
    assert "naive" in results
    assert "moving_average" in results
    for r in results.values():
        assert r.mae >= 0
        assert r.rmse >= 0


def test_pick_best_selects_lowest_rmse(synthetic_monthly_df):
    series = synthetic_monthly_df["count"].astype(float)
    results = evaluate_models(series)
    best = pick_best(results)
    assert best in results
    assert all(results[best].rmse <= r.rmse for r in results.values())


def test_forecast_future_produces_horizon_length(synthetic_monthly_df):
    series = synthetic_monthly_df["count"].astype(float)
    mean, lower, upper = forecast_future(series, "naive", horizon=6)
    assert len(mean) == 6


def test_arima_confidence_interval_present_when_available(synthetic_monthly_df):
    series = synthetic_monthly_df["count"].astype(float)
    mean, lower, upper = forecast_future(series, "arima", horizon=3)
    assert len(mean) == 3
    # CI may be None only if ARIMA itself failed to fit (defensive fallback);
    # with 30 points of well-behaved synthetic data it should fit successfully.
    if lower is not None:
        assert len(lower) == 3
        assert len(upper) == 3


def test_evaluate_models_handles_too_short_series():
    series = pd.Series([1, 2, 3])
    results = evaluate_models(series)
    assert results == {}
