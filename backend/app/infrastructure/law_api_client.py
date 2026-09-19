"""HTTP client for the law.go.kr Open API (국가법령정보센터).

Docs:
- List search: https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precListGuide
- Detail:      https://open.law.go.kr/LSO/openApi/guideResult.do?htmlName=precInfoGuide

This client NEVER fabricates data. If the API key is missing or every retry
attempt fails, it raises `LawApiBlockedError` with an actionable message
prefixed with [BLOCKED].
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx

from app.config import settings

LIST_URL = "http://www.law.go.kr/DRF/lawSearch.do"
DETAIL_URL = "http://www.law.go.kr/DRF/lawService.do"

RETRY_DELAYS = (1, 2, 4, 8)  # seconds, exponential backoff
DEFAULT_TIMEOUT = 15.0
RATE_LIMIT_DELAY = 0.3  # polite delay between successive requests


class LawApiBlockedError(RuntimeError):
    """Raised whenever real data cannot be obtained. Never caught to fabricate data."""


@dataclass
class LawApiClient:
    oc: str
    timeout: float = DEFAULT_TIMEOUT
    max_retries: int = len(RETRY_DELAYS)
    rate_limit_delay: float = RATE_LIMIT_DELAY
    _client: httpx.Client | None = None

    def __post_init__(self) -> None:
        if not self.oc:
            raise LawApiBlockedError(
                "[BLOCKED] LAW_API_OC missing. Set LAW_API_OC in .env "
                "(see .env.example) using your law.go.kr Open API OC id."
            )
        self._client = httpx.Client(timeout=self.timeout)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> "LawApiClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    def _get_with_retry(self, url: str, params: dict[str, Any]) -> dict[str, Any]:
        assert self._client is not None
        last_exc: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                resp = self._client.get(url, params=params)
                resp.raise_for_status()
                # law.go.kr serves this endpoint as EUC-KR bytes without a
                # charset declared in Content-Type, so httpx/resp.json() (which
                # assumes UTF-8) mangles every Korean field. Decode explicitly,
                # trying EUC-KR first (the documented encoding for this API)
                # and falling back to UTF-8 for any endpoint that does return it.
                text: str | None = None
                for encoding in ("euc-kr", "utf-8"):
                    try:
                        text = resp.content.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                if text is None:
                    text = resp.content.decode("utf-8", errors="replace")
                try:
                    data = json.loads(text)
                except ValueError as exc:
                    raise LawApiBlockedError(
                        "[BLOCKED] law.go.kr returned a non-JSON response "
                        "(often an HTML auth-error page). Check that LAW_API_OC "
                        "is a valid, activated OC id."
                    ) from exc
                time.sleep(self.rate_limit_delay)
                return data
            except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                break
        raise LawApiBlockedError(
            f"[BLOCKED] law.go.kr request failed after {self.max_retries + 1} attempts: "
            f"{last_exc}. Action: verify network access and LAW_API_OC, then retry."
        ) from last_exc

    def search_precedents(
        self,
        query: str,
        page: int = 1,
        display: int = 100,
        search: int = 1,
        org: str | None = None,
        curt: str | None = None,
        prnc_yd: str | None = None,
        sort: str | None = None,
    ) -> dict[str, Any]:
        """Call lawSearch.do?target=prec. Returns the raw parsed JSON dict."""
        params: dict[str, Any] = {
            "OC": self.oc,
            "target": "prec",
            "type": "JSON",
            "search": search,
            "query": query,
            "display": display,
            "page": page,
        }
        if org:
            params["org"] = org
        if curt:
            params["curt"] = curt
        if prnc_yd:
            params["prncYd"] = prnc_yd
        if sort:
            params["sort"] = sort
        return self._get_with_retry(LIST_URL, params)

    def get_precedent_detail(self, precedent_id: str) -> dict[str, Any]:
        """Call lawService.do?target=prec for full body text of one precedent."""
        params = {
            "OC": self.oc,
            "target": "prec",
            "type": "JSON",
            "ID": precedent_id,
        }
        return self._get_with_retry(DETAIL_URL, params)


def build_client() -> LawApiClient:
    """Factory that raises LawApiBlockedError with a clear message if unconfigured."""
    return LawApiClient(oc=settings.law_api_oc)


def total_pages(total_cnt: int, display: int) -> int:
    """Pagination math: number of pages needed to cover total_cnt records."""
    if display <= 0:
        return 0
    return (total_cnt + display - 1) // display
