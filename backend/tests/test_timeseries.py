from __future__ import annotations

import pandas as pd

from app.services.precedent_service import dedupe, normalize_raw_payload
from app.services.timeseries_service import (
    court_counts,
    keyword_monthly_counts,
    monthly_counts,
    yearly_counts,
)
from app.utils.dates import parse_law_date, quarter_of


def test_parse_law_date_formats():
    assert parse_law_date("20200115").isoformat() == "2020-01-15"
    assert parse_law_date("2020.01.15").isoformat() == "2020-01-15"
    assert parse_law_date(None) is None
    assert parse_law_date("garbage") is None


def test_quarter_of():
    assert quarter_of(1) == 1
    assert quarter_of(3) == 1
    assert quarter_of(4) == 2
    assert quarter_of(12) == 4


def test_dedup_by_precedent_id(fixture_list_payload):
    records = normalize_raw_payload(fixture_list_payload, "계약")
    duped = records + records  # duplicate the same 3
    out = dedupe(duped)
    assert len(out) == 3


def _sample_df():
    df = pd.DataFrame(
        {
            "decision_date": pd.to_datetime(
                ["2022-01-05", "2022-01-20", "2022-02-01", "2023-01-10", None]
            ),
            "search_keyword": ["계약", "계약", "손해배상", "계약", "계약"],
            "court_type": ["대법원", "지방/기타", "지방/기타", "대법원", "지방/기타"],
        }
    )
    return df


def test_monthly_counts_fills_gaps_and_handles_missing():
    df = _sample_df()
    out = monthly_counts(df)
    # Missing decision_date rows are dropped, gaps between Jan2022..Jan2023 are filled with 0
    assert out["period"].iloc[0] == "2022-01"
    assert out["period"].iloc[-1] == "2023-01"
    assert len(out) == 13  # Jan2022 through Jan2023 inclusive
    assert out.loc[out["period"] == "2022-01", "count"].iloc[0] == 2


def test_yearly_counts():
    df = _sample_df()
    out = yearly_counts(df)
    assert out.set_index("year")["count"].to_dict() == {2022: 3, 2023: 1}


def test_keyword_monthly_counts():
    df = _sample_df()
    out = keyword_monthly_counts(df)
    row = out[(out["period"] == "2022-01") & (out["search_keyword"] == "계약")]
    assert row["count"].iloc[0] == 2


def test_court_counts():
    df = _sample_df()
    out = court_counts(df)
    assert set(out["court_type"]) == {"대법원", "지방/기타"}
