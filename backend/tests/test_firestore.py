"""Tests for Firestore integration.

No real network/credentials are used - a fake client verifies the code
writes to the right collections with the right document shape, and that
every function degrades to a clear {"saved"/"available": False, "reason"}
result (never an exception) when Firestore isn't configured.
"""
from __future__ import annotations

from app.infrastructure import firestore_client
from app.services import firestore_service


def test_unconfigured_status_is_clear(monkeypatch):
    monkeypatch.setattr("app.config.settings.firebase_credentials_json", "")
    monkeypatch.setattr(firestore_client, "_client", None)
    monkeypatch.setattr(firestore_client, "_init_attempted", False)
    status = firestore_client.firestore_status()
    assert status["configured"] is False
    assert "FIREBASE_CREDENTIALS_JSON" in status["reason"]


def test_save_analysis_snapshot_without_config_does_not_raise(monkeypatch):
    monkeypatch.setattr("app.config.settings.firebase_credentials_json", "")
    monkeypatch.setattr(firestore_client, "_client", None)
    monkeypatch.setattr(firestore_client, "_init_attempted", False)
    result = firestore_service.save_analysis_snapshot({"total_records": 10})
    assert result["saved"] is False
    assert "FIREBASE_CREDENTIALS_JSON" in result["reason"]


class _FakeDocRef:
    def __init__(self, store: dict, key):
        self._store = store
        self._key = key

    def set(self, data):
        self._store[self._key] = data


class _FakeCollection:
    def __init__(self, store: dict):
        self._store = store

    def document(self, doc_id):
        return _FakeDocRef(self._store, doc_id)


class _FakeClient:
    def __init__(self):
        self.collections: dict[str, dict] = {}

    def collection(self, name):
        self.collections.setdefault(name, {})
        return _FakeCollection(self.collections[name])


def test_save_analysis_snapshot_writes_to_data_collection(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(firestore_service, "get_firestore_client", lambda: fake)

    result = firestore_service.save_analysis_snapshot(
        {"collected_at": "2026-01-01T00:00:00", "total_records": 42}
    )

    assert result["saved"] is True
    saved_doc = fake.collections["data"][result["doc_id"]]
    assert saved_doc["total_records"] == 42
    assert "saved_at" in saved_doc


def test_save_conversation_turn_writes_to_conversations_collection(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(firestore_service, "get_firestore_client", lambda: fake)

    result = firestore_service.save_conversation_turn(
        session_id="abc",
        user_message="이상치가 몇 개야?",
        answer="7건입니다.",
        tool_calls=[{"name": "get_anomalies", "arguments": {}, "error": None}],
        available=True,
    )

    assert result["saved"] is True
    docs = list(fake.collections["conversations"].values())
    assert len(docs) == 1
    assert docs[0]["session_id"] == "abc"
    assert docs[0]["answer"] == "7건입니다."
    assert docs[0]["tool_calls"][0]["name"] == "get_anomalies"
