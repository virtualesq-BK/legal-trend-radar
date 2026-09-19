from __future__ import annotations

import pandas as pd

from app.services.trend_service import (
    add_moving_averages,
    add_volatility,
    add_yoy_change,
    build_trend_table,
)


def test_moving_averages():
    df = pd.DataFrame({"period": [f"m{i}" for i in range(5)], "count": [10, 20, 30, 40, 50]})
    out = add_moving_averages(df)
    assert out["ma_3m"].iloc[2] == 20  # mean(10,20,30)
    assert out["ma_3m"].iloc[0] == 10  # min_periods=1


def test_yoy_change():
    df = pd.DataFrame({"period": [f"m{i}" for i in range(13)], "count": [10] * 12 + [15]})
    out = add_yoy_change(df)
    assert round(out["yoy_pct_change"].iloc[12], 2) == 50.0
    assert pd.isna(out["yoy_pct_change"].iloc[5])


def test_volatility_is_rolling_std():
    df = pd.DataFrame({"period": ["a", "b", "c"], "count": [10, 20, 10]})
    out = add_volatility(df, window=3)
    assert abs(out["volatility"].iloc[-1] - df["count"].std()) < 1e-9


def test_build_trend_table_has_all_columns():
    df = pd.DataFrame({"period": [f"m{i}" for i in range(14)], "count": list(range(14))})
    out = build_trend_table(df)
    for col in ["ma_3m", "ma_12m", "yoy_pct_change", "volatility"]:
        assert col in out.columns
