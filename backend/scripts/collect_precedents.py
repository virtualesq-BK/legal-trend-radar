#!/usr/bin/env python
"""Collect precedents from law.go.kr for the configured keywords/date range.

Saves raw JSON page responses to backend/data/raw/<keyword>_<page>.json.
NEVER fabricates data: on missing key or unrecoverable API failure it prints
a [BLOCKED] message with the required action and exits nonzero.

Usage:
    python backend/scripts/collect_precedents.py --start-date 2016-01-01 \
        --end-date 2026-12-31 --keywords 계약,손해배상 --display 100 --max-pages 5
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import DATA_RAW_DIR, settings  # noqa: E402
from app.infrastructure.law_api_client import (  # noqa: E402
    LawApiBlockedError,
    build_client,
    total_pages,
)
from app.utils.dates import to_prnc_yd  # noqa: E402
from app.utils.logging import get_logger  # noqa: E402

logger = get_logger("collect_precedents")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect precedents from law.go.kr")
    p.add_argument("--start-date", default=settings.default_start_date)
    p.add_argument("--end-date", default=settings.default_end_date)
    p.add_argument("--keywords", default=",".join(settings.default_keywords))
    p.add_argument("--display", type=int, default=100)
    p.add_argument("--max-pages", type=int, default=50)
    p.add_argument("--include-body", action="store_true")
    p.add_argument("--body-limit", type=int, default=50)
    p.add_argument("--resume", action="store_true")
    return p.parse_args()


def raw_path(keyword: str, page: int) -> Path:
    safe_kw = keyword.replace("/", "_")
    return DATA_RAW_DIR / f"{safe_kw}_page{page}.json"


def collect_keyword(client, keyword: str, args: argparse.Namespace) -> int:
    prnc_yd = to_prnc_yd(args.start_date, args.end_date)
    page = 1
    total_saved = 0
    total_cnt = None
    while True:
        if args.max_pages and page > args.max_pages:
            logger.info("Reached --max-pages=%s for keyword=%s", args.max_pages, keyword)
            break
        out_path = raw_path(keyword, page)
        if args.resume and out_path.exists():
            logger.info("Resume: skipping already-downloaded %s", out_path)
            with open(out_path, encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = client.search_precedents(
                query=keyword, page=page, display=args.display, prnc_yd=prnc_yd
            )
            DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Saved page %s for keyword=%s -> %s", page, keyword, out_path)

        root = data.get("PrecSearch") or data.get("precSearch") or data
        if total_cnt is None:
            try:
                total_cnt = int(root.get("totalCnt", 0))
            except (TypeError, ValueError):
                total_cnt = 0
        total_saved += 1
        pages_needed = total_pages(total_cnt, args.display)
        if page >= pages_needed:
            break
        page += 1
    return total_saved


def main() -> int:
    args = parse_args()
    try:
        client = build_client()
    except LawApiBlockedError as exc:
        print(str(exc))
        return 2

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    try:
        with client:
            for kw in keywords:
                logger.info("Collecting keyword: %s", kw)
                collect_keyword(client, kw, args)
    except LawApiBlockedError as exc:
        print(str(exc))
        return 2

    print(f"Collection complete. Raw pages saved to {DATA_RAW_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
