from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402
import pytest  # noqa: E402


def make_prec_record(pid: str, date: str, case_name: str = "테스트 사건", court: str = "서울중앙지방법원"):
    return {
        "판례일련번호": pid,
        "사건명": case_name,
        "사건번호": f"2020가합{pid}",
        "선고일자": date,
        "법원명": court,
        "사건종류명": "민사",
        "판결유형": "판결",
        "판례상세링크": f"/DRF/lawService.do?ID={pid}",
    }


@pytest.fixture
def fixture_list_payload():
    """Small synthetic JSON shaped like a real lawSearch.do?target=prec response."""
    return {
        "PrecSearch": {
            "totalCnt": "3",
            "page": "1",
            "prec": [
                make_prec_record("100001", "20200115"),
                make_prec_record("100002", "20200220"),
                make_prec_record("100003", "20200305"),
            ],
        }
    }


@pytest.fixture
def synthetic_monthly_df():
    import numpy as np

    periods = pd.period_range("2022-01", periods=30, freq="M").astype(str)
    rng = np.random.default_rng(42)
    counts = (20 + 5 * np.sin(np.arange(30) * 2 * np.pi / 12) + rng.normal(0, 2, 30)).round().astype(int)
    counts = counts.clip(min=0)
    counts[10] = 200  # inject an obvious anomaly
    return pd.DataFrame({"period": periods, "count": counts})
