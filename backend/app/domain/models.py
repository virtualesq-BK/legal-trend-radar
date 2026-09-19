"""Core domain dataclass for a normalized precedent record."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Precedent:
    precedent_id: str
    case_name: str
    case_number: str
    decision_date: date | None
    decision_year: int | None
    decision_month: int | None
    decision_quarter: int | None
    court_name: str
    court_type: str
    case_type: str
    judgment_type: str
    search_keyword: str
    source: str = "law.go.kr"
    source_url: str = ""
    collected_at: datetime = field(default_factory=datetime.utcnow)
    points_at_issue: str = ""
    judgment_summary: str = ""
    precedent_content: str = ""

    def dedupe_key(self) -> str:
        if self.precedent_id:
            return f"id:{self.precedent_id}"
        dd = self.decision_date.isoformat() if self.decision_date else "unknown"
        return f"cn:{self.case_number}|{dd}|{self.case_name}"
