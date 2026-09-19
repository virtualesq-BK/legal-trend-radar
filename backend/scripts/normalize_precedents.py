#!/usr/bin/env python
"""Normalize raw law.go.kr JSON pages into clean, deduped precedent records.

Reads backend/data/raw/*.json, writes backend/data/processed/precedents.{parquet,csv}.
Validates minimum record counts; NEVER fabricates data to satisfy validation.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_PROCESSED_DIR, DATA_RAW_DIR, settings  # noqa: E402
from app.services.precedent_service import dedupe, normalize_raw_payload  # noqa: E402
from app.utils.logging import get_logger  # noqa: E402

logger = get_logger("normalize_precedents")

MIN_RECORDS = settings.min_records_required
MIN_UNIQUE_IDS = settings.min_records_required
MIN_VALID_DATE_RATIO = 0.95


def keyword_from_filename(path: Path) -> str:
    # filenames are "<keyword>_page<N>.json"
    stem = path.stem
    return stem.rsplit("_page", 1)[0]


def main() -> int:
    raw_files = sorted(DATA_RAW_DIR.glob("*.json"))
    if not raw_files:
        print(
            "[BLOCKED] No raw data found in backend/data/raw/. "
            "Action: run collect_precedents.py after setting LAW_API_OC in .env."
        )
        return 2

    all_records = []
    for path in raw_files:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
        kw = keyword_from_filename(path)
        all_records.extend(normalize_raw_payload(raw, kw))

    records = dedupe(all_records)
    n = len(records)
    unique_ids = len({r.precedent_id for r in records if r.precedent_id})
    valid_dates = sum(1 for r in records if r.decision_date is not None)
    valid_ratio = valid_dates / n if n else 0.0

    df = pd.DataFrame([asdict(r) for r in records])

    ok = True
    if n < MIN_RECORDS:
        print(f"[WARNING] Only {n} records found; minimum required is {MIN_RECORDS}.")
        ok = False
    if unique_ids < MIN_UNIQUE_IDS and n >= MIN_RECORDS:
        print(f"[WARNING] Only {unique_ids} unique precedent_id values; minimum required is {MIN_UNIQUE_IDS}.")
        ok = False
    if valid_ratio < MIN_VALID_DATE_RATIO:
        print(f"[WARNING] Only {valid_ratio:.1%} of records have a valid decision_date (need >=95%).")
        ok = False

    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if n > 0:
        df.to_csv(DATA_PROCESSED_DIR / "precedents.csv", index=False)
        try:
            df.to_parquet(DATA_PROCESSED_DIR / "precedents.parquet", index=False)
        except Exception as exc:  # pyarrow optional at runtime
            logger.warning("Could not write parquet (%s); CSV written instead.", exc)

    print(f"Normalized {n} records ({unique_ids} unique ids, {valid_ratio:.1%} valid dates).")
    if not ok:
        print("Validation thresholds NOT met - see warnings above. Data was still written as-is (no fabrication).")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
