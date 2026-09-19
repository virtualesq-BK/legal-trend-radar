"""Normalize raw law.go.kr JSON list-search records into `Precedent` objects."""
from __future__ import annotations

from typing import Any, Iterable

from app.domain.models import Precedent
from app.utils.dates import parse_law_date, quarter_of

# law.go.kr list-search JSON commonly nests results under "PrecSearch" -> "prec"
# (a list, or a single dict when there is exactly one hit). Field names below
# match the documented precListGuide response.
FIELD_MAP = {
    "precedent_id": ["판례일련번호", "id", "precId"],
    "case_name": ["사건명", "caseNm"],
    "case_number": ["사건번호", "caseNo"],
    "decision_date": ["선고일자", "judmntDate"],
    "court_name": ["법원명", "courtNm"],
    "case_type": ["사건종류명", "caseType"],
    "judgment_type": ["판결유형", "judmntType"],
    "source_url": ["판례상세링크", "detailLink"],
}


def _first(rec: dict[str, Any], keys: list[str]) -> str:
    for k in keys:
        if k in rec and rec[k] not in (None, ""):
            return str(rec[k])
    return ""


def _extract_prec_list(raw: dict[str, Any]) -> list[dict[str, Any]]:
    root = raw.get("PrecSearch") or raw.get("precSearch") or raw
    items = root.get("prec") if isinstance(root, dict) else None
    if items is None:
        return []
    if isinstance(items, dict):
        return [items]
    if isinstance(items, list):
        return items
    return []


def normalize_record(rec: dict[str, Any], search_keyword: str) -> Precedent:
    case_name = _first(rec, FIELD_MAP["case_name"])
    case_number = _first(rec, FIELD_MAP["case_number"])
    precedent_id = _first(rec, FIELD_MAP["precedent_id"])
    date_raw = _first(rec, FIELD_MAP["decision_date"])
    d = parse_law_date(date_raw)
    court_name = _first(rec, FIELD_MAP["court_name"])
    court_type = "대법원" if "대법원" in court_name else ("고등법원" if "고등" in court_name else "지방/기타")
    return Precedent(
        precedent_id=precedent_id,
        case_name=case_name,
        case_number=case_number,
        decision_date=d,
        decision_year=d.year if d else None,
        decision_month=d.month if d else None,
        decision_quarter=quarter_of(d.month) if d else None,
        court_name=court_name,
        court_type=court_type,
        case_type=_first(rec, FIELD_MAP["case_type"]),
        judgment_type=_first(rec, FIELD_MAP["judgment_type"]),
        search_keyword=search_keyword,
        source="law.go.kr",
        source_url=_first(rec, FIELD_MAP["source_url"]),
        points_at_issue=str(rec.get("판시사항", "")),
        judgment_summary=str(rec.get("판결요지", "")),
        precedent_content=str(rec.get("판례내용", "")),
    )


def normalize_raw_payload(raw: dict[str, Any], search_keyword: str) -> list[Precedent]:
    return [normalize_record(r, search_keyword) for r in _extract_prec_list(raw)]


def dedupe(records: Iterable[Precedent]) -> list[Precedent]:
    seen: set[str] = set()
    out: list[Precedent] = []
    for r in records:
        k = r.dedupe_key()
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out
