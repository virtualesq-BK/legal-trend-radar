from __future__ import annotations

import httpx
import pytest

from app.infrastructure.law_api_client import LawApiBlockedError, LawApiClient, total_pages
from app.services.precedent_service import normalize_raw_payload


def test_missing_oc_raises_blocked():
    with pytest.raises(LawApiBlockedError):
        LawApiClient(oc="")


def test_total_pages_math():
    assert total_pages(0, 100) == 0
    assert total_pages(100, 100) == 1
    assert total_pages(101, 100) == 2
    assert total_pages(250, 100) == 3


def test_search_precedents_parses_json(monkeypatch, fixture_list_payload):
    client = LawApiClient(oc="test-oc")

    def fake_get(self, url, params=None, **kwargs):
        return httpx.Response(200, json=fixture_list_payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", fake_get)
    data = client.search_precedents(query="계약", page=1, display=100)
    records = normalize_raw_payload(data, "계약")
    assert len(records) == 3
    assert records[0].precedent_id == "100001"
    client.close()


def test_retry_then_success(monkeypatch, fixture_list_payload):
    client = LawApiClient(oc="test-oc", rate_limit_delay=0)
    calls = {"n": 0}

    def flaky_get(self, url, params=None, **kwargs):
        calls["n"] += 1
        if calls["n"] < 2:
            raise httpx.TransportError("boom")
        return httpx.Response(200, json=fixture_list_payload, request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", flaky_get)
    monkeypatch.setattr("time.sleep", lambda s: None)
    data = client.search_precedents(query="계약")
    assert calls["n"] == 2
    assert data["PrecSearch"]["totalCnt"] == "3"
    client.close()


def test_exhausted_retries_raise_blocked(monkeypatch):
    client = LawApiClient(oc="test-oc", max_retries=1, rate_limit_delay=0)

    def always_fail(self, url, params=None, **kwargs):
        raise httpx.TransportError("down")

    monkeypatch.setattr(httpx.Client, "get", always_fail)
    monkeypatch.setattr("time.sleep", lambda s: None)
    with pytest.raises(LawApiBlockedError):
        client.search_precedents(query="계약")
    client.close()


def test_non_json_response_raises_blocked(monkeypatch):
    client = LawApiClient(oc="test-oc", rate_limit_delay=0)

    def bad_json_get(self, url, params=None, **kwargs):
        return httpx.Response(200, content=b"<html>not json</html>", request=httpx.Request("GET", url))

    monkeypatch.setattr(httpx.Client, "get", bad_json_get)
    with pytest.raises(LawApiBlockedError):
        client.search_precedents(query="계약")
    client.close()
