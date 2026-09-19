"""Date parsing helpers shared across the pipeline."""
from __future__ import annotations

from datetime import date, datetime

# law.go.kr commonly returns decision dates as YYYYMMDD or YYYY.MM.DD strings.
_FORMATS = ("%Y%m%d", "%Y.%m.%d", "%Y-%m-%d")


def parse_law_date(raw: str | None) -> date | None:
    """Parse a law.go.kr date string. Returns None (never raises) on bad input."""
    if not raw:
        return None
    raw = str(raw).strip()
    if not raw:
        return None
    for fmt in _FORMATS:
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


def quarter_of(month: int) -> int:
    return (month - 1) // 3 + 1


def to_prnc_yd(start: str, end: str) -> str:
    """Build the prncYd=YYYYMMDD~YYYYMMDD range param from ISO dates."""
    s = datetime.strptime(start, "%Y-%m-%d").strftime("%Y%m%d")
    e = datetime.strptime(end, "%Y-%m-%d").strftime("%Y%m%d")
    return f"{s}~{e}"
