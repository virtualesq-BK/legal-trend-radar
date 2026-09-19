from __future__ import annotations

import pandas as pd

from app.services.anomaly_service import combined_anomalies, detect_iqr, detect_zscore


def test_zscore_flags_obvious_outlier():
    counts = [10] * 11 + [1000]
    df = pd.DataFrame({"period": [f"m{i}" for i in range(12)], "count": counts})
    out = detect_zscore(df, threshold=2.0)
    assert out["is_anomaly"].iloc[-1]
    assert not out["is_anomaly"].iloc[0]
    assert (out["method"] == "zscore").all()


def test_iqr_flags_obvious_outlier():
    counts = [10, 12, 9, 11, 10, 13, 8, 1000]
    df = pd.DataFrame({"period": [f"m{i}" for i in range(8)], "count": counts})
    out = detect_iqr(df, k=1.5)
    assert out["is_anomaly"].iloc[-1]
    assert (out["method"] == "iqr").all()


def test_zscore_handles_constant_series_without_div_by_zero():
    df = pd.DataFrame({"period": ["a", "b", "c"], "count": [5, 5, 5]})
    out = detect_zscore(df)
    assert not out["is_anomaly"].any()


def test_combined_anomalies_has_both_methods():
    df = pd.DataFrame({"period": [f"m{i}" for i in range(10)], "count": [10] * 9 + [500]})
    out = combined_anomalies(df)
    assert set(out["method"]) == {"zscore", "iqr"}
    for col in ["threshold", "score", "is_anomaly"]:
        assert col in out.columns
