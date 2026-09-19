from __future__ import annotations

import pytest

from app.services.decomposition_service import InsufficientDataError, run_stl


def test_stl_runs_on_sufficient_data(synthetic_monthly_df):
    out = run_stl(synthetic_monthly_df, period=12, robust=True)
    assert len(out) == len(synthetic_monthly_df)
    for col in ["observed", "trend", "seasonal", "resid"]:
        assert col in out.columns
        assert out[col].notna().all()


def test_stl_raises_on_insufficient_data():
    import pandas as pd

    short_df = pd.DataFrame({"period": [f"2022-{i:02d}" for i in range(1, 6)], "count": [1, 2, 3, 4, 5]})
    with pytest.raises(InsufficientDataError):
        run_stl(short_df, period=12)
