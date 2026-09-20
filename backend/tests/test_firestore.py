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


class _FakeSnapshot:
    def __init__(self, doc_id, data):
        self.id = doc_id
        self._data = data

    def to_dict(self):
        return dict(self._data)

    @property
    def exists(self):
        return self._data is not None


class _FakeDocRef:
    def __init__(self, store: dict, key):
        self._store = store
        self._key = key

    def set(self, data):
        self._store[self._key] = data

    def get(self):
        return _FakeSnapshot(self._key, self._store.get(self._key))

    def update(self, data):
        self._store[self._key] = {**self._store[self._key], **data}

    def delete(self):
        self._store.pop(self._key, None)


class _FakeQuery:
    def __init__(self, store: dict, field=None, value=None):
        self._store = store
        self._field = field
        self._value = value

    def where(self, *args, filter=None, **kwargs):  # noqa: A002 - match real API's kwarg name
        field, _, value = filter.field_path, filter.op_string, filter.value if filter else (None, None, None)
        return _FakeQuery(self._store, field, value)

    def stream(self):
        for doc_id, data in self._store.items():
            if self._field is None or data.get(self._field) == self._value:
                yield _FakeSnapshot(doc_id, data)


class _FakeCollection(_FakeQuery):
    def __init__(self, store: dict):
        super().__init__(store)

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


def test_data_record_crud_lifecycle(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(firestore_service, "get_firestore_client", lambda: fake)

    created = firestore_service.create_data_record("2026-01-01", 10.0, "메모")
    assert created["saved"] is True
    record_id = created["id"]

    listed = firestore_service.list_data_records()
    assert listed["available"] is True
    assert len(listed["records"]) == 1
    assert listed["records"][0]["value"] == 10.0

    updated = firestore_service.update_data_record(record_id, None, 20.0, None)
    assert updated["saved"] is True
    listed_again = firestore_service.list_data_records()
    assert listed_again["records"][0]["value"] == 20.0
    assert listed_again["records"][0]["memo"] == "메모"  # untouched field preserved

    deleted = firestore_service.delete_data_record(record_id)
    assert deleted["saved"] is True
    assert firestore_service.list_data_records()["records"] == []


def test_update_nonexistent_record_returns_not_found(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(firestore_service, "get_firestore_client", lambda: fake)

    result = firestore_service.update_data_record("missing-id", "2026-01-01", 1.0, None)
    assert result["saved"] is False
    assert "not found" in result["reason"]


def test_list_conversation_sessions_groups_by_session(monkeypatch):
    fake = _FakeClient()
    monkeypatch.setattr(firestore_service, "get_firestore_client", lambda: fake)

    firestore_service.save_conversation_turn("s1", "q1", "a1", [], True)
    firestore_service.save_conversation_turn("s1", "q2", "a2", [], True)
    firestore_service.save_conversation_turn("s2", "q3", "a3", [], True)

    result = firestore_service.list_conversation_sessions()
    assert result["available"] is True
    by_id = {s["session_id"]: s for s in result["sessions"]}
    assert by_id["s1"]["turn_count"] == 2
    assert by_id["s1"]["last_message"] == "q2"
    assert by_id["s2"]["turn_count"] == 1
