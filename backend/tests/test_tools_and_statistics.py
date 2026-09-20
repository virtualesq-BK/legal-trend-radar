"""Tests for the function-calling tool registry and enriched statistics.

These check pure computation and registry shape - no network/LLM calls.
"""
from __future__ import annotations

import pandas as pd

from app.services.statistics_service import compute_statistics
from app.services.tools_service import TOOL_FUNCTIONS, TOOL_SPECS


def _monthly():
    return pd.DataFrame(
        {
            "period": ["2020-01", "2020-02", "2020-03", "2020-04"],
            "count": [10, 20, 100, 15],
        }
    )


def _anomalies():
    return pd.DataFrame(
        {
            "period": ["2020-01", "2020-02", "2020-03", "2020-04"],
            "is_anomaly": [False, False, True, False],
        }
    )


def test_compute_statistics_basic_fields():
    stats = compute_statistics(_monthly(), _anomalies())
    assert stats["total_months"] == 4
    assert stats["total_count"] == 145
    assert stats["peak_month"]["period"] == "2020-03"
    assert stats["trough_month"]["period"] == "2020-01"
    assert stats["anomaly_rate_pct"] == 25.0
    # growth rate: (15 - 10) / 10 * 100
    assert round(stats["growth_rate_pct_full_period"], 2) == 50.0


def test_compute_statistics_empty_is_safe():
    empty = pd.DataFrame({"period": [], "count": []})
    stats = compute_statistics(empty, empty.assign(is_anomaly=[]))
    assert stats["total_months"] == 0
    assert stats["peak_month"] is None
    assert stats["growth_rate_pct_full_period"] is None


def test_tool_specs_match_tool_functions():
    spec_names = {spec["function"]["name"] for spec in TOOL_SPECS}
    assert spec_names == set(TOOL_FUNCTIONS.keys())
    for spec in TOOL_SPECS:
        fn = spec["function"]
        assert fn["name"]
        assert fn["description"]
        assert "parameters" in fn and fn["parameters"]["type"] == "object"


def test_tool_get_statistics_uses_real_repository(monkeypatch):
    from app.services import tools_service

    monkeypatch.setattr(tools_service, "load_monthly", _monthly)
    monkeypatch.setattr(tools_service, "load_anomalies", _anomalies)
    result = tools_service.tool_get_statistics()
    assert result["total_months"] == 4
