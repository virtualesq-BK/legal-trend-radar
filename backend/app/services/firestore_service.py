"""Firestore persistence for Legal Trend Radar.

Collection design:

- `data`         : holds two kinds of document, distinguished by a `kind`
                    field so they can share one collection (matching the
                    "data: 분석 데이터 저장" spec) while staying queryable
                    separately:
                      - kind="snapshot": one document per full pipeline run
                        (precedent summary + monthly/yearly trend + enriched
                        statistics + forecast metrics), doc ID = collected_at
                        timestamp. Written by scripts/sync_firestore.py.
                      - kind="record": one document per user-managed
                        (date, value, memo) data point, created/edited/
                        deleted through the CRUD API
                        (`app/api/routes/data_records.py`) and summarized by
                        the `get_saved_data_summary` chat tool.
- `conversations`: one document per chat turn (question + tool calls +
                    answer), grouped by `session_id` so a UI can list past
                    conversations and reload a specific one.

All of this is optional/best-effort: if Firestore isn't configured
(`FIREBASE_CREDENTIALS_JSON` unset) or a write fails, callers get back a
clear {"saved"/"available": False, "reason": ...} instead of an exception -
persistence here is an add-on, never a blocker for the core pipeline/API/chat.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.infrastructure.firestore_client import FirestoreUnavailableError, get_firestore_client


def save_analysis_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Write one analysis snapshot to the `data` collection (kind="snapshot").

    `snapshot` should already be the real, computed pipeline output (e.g.
    precedent summary + monthly/yearly trend + statistics + forecast
    metrics) - this function does not compute or fabricate anything, only
    persists what it's given.
    """
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"saved": False, "reason": str(exc)}

    doc_id = snapshot.get("collected_at") or datetime.now(timezone.utc).isoformat()
    doc_id = str(doc_id).replace(":", "-").replace(" ", "_")
    try:
        client.collection(settings.firestore_data_collection).document(doc_id).set(
            {**snapshot, "kind": "snapshot", "saved_at": datetime.now(timezone.utc).isoformat()}
        )
        return {"saved": True, "reason": None, "doc_id": doc_id}
    except Exception as exc:  # noqa: BLE001 - never let a Firestore hiccup break the caller
        return {"saved": False, "reason": f"Firestore write failed: {exc}"}


# --- (date, value, memo) CRUD records -------------------------------------


def create_data_record(date: str, value: float, memo: str | None = None) -> dict[str, Any]:
    """Create one (date, value, memo) record in the `data` collection (kind="record")."""
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"saved": False, "reason": str(exc)}

    doc_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()
    doc = {"kind": "record", "date": date, "value": value, "memo": memo, "created_at": now, "updated_at": now}
    try:
        client.collection(settings.firestore_data_collection).document(doc_id).set(doc)
        return {"saved": True, "reason": None, "id": doc_id, "record": {**doc, "id": doc_id}}
    except Exception as exc:  # noqa: BLE001
        return {"saved": False, "reason": f"Firestore write failed: {exc}"}


def list_data_records() -> dict[str, Any]:
    """List all (date, value, memo) records, sorted by date ascending."""
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"available": False, "reason": str(exc), "records": []}

    try:
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = client.collection(settings.firestore_data_collection).where(
            filter=FieldFilter("kind", "==", "record")
        )
        records = []
        for doc in query.stream():
            data = doc.to_dict()
            data["id"] = doc.id
            records.append(data)
        records.sort(key=lambda r: r.get("date") or "")
        return {"available": True, "reason": None, "records": records}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"Firestore read failed: {exc}", "records": []}


def update_data_record(record_id: str, date: str | None, value: float | None, memo: str | None) -> dict[str, Any]:
    """Patch an existing record. Only non-None fields are updated."""
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"saved": False, "reason": str(exc)}

    updates: dict[str, Any] = {"updated_at": datetime.now(timezone.utc).isoformat()}
    if date is not None:
        updates["date"] = date
    if value is not None:
        updates["value"] = value
    if memo is not None:
        updates["memo"] = memo
    try:
        ref = client.collection(settings.firestore_data_collection).document(record_id)
        if not ref.get().exists:
            return {"saved": False, "reason": f"Record {record_id} not found"}
        ref.update(updates)
        return {"saved": True, "reason": None}
    except Exception as exc:  # noqa: BLE001
        return {"saved": False, "reason": f"Firestore write failed: {exc}"}


def delete_data_record(record_id: str) -> dict[str, Any]:
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"saved": False, "reason": str(exc)}

    try:
        ref = client.collection(settings.firestore_data_collection).document(record_id)
        if not ref.get().exists:
            return {"saved": False, "reason": f"Record {record_id} not found"}
        ref.delete()
        return {"saved": True, "reason": None}
    except Exception as exc:  # noqa: BLE001
        return {"saved": False, "reason": f"Firestore write failed: {exc}"}


def save_conversation_turn(
    session_id: str,
    user_message: str,
    answer: str | None,
    tool_calls: list[dict[str, Any]],
    available: bool,
) -> dict[str, Any]:
    """Append one chat turn to the `conversations` collection."""
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"saved": False, "reason": str(exc)}

    doc = {
        "session_id": session_id,
        "user_message": user_message,
        "answer": answer,
        "tool_calls": tool_calls,
        "available": available,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        client.collection(settings.firestore_conversations_collection).document(str(uuid.uuid4())).set(doc)
        return {"saved": True, "reason": None}
    except Exception as exc:  # noqa: BLE001
        return {"saved": False, "reason": f"Firestore write failed: {exc}"}


def list_conversation_history(session_id: str, limit: int = 20) -> dict[str, Any]:
    """Read back the most recent turns for a session, oldest first."""
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"available": False, "reason": str(exc), "turns": []}

    try:
        # Filter on session_id only (single-field, auto-indexed by Firestore)
        # and sort/limit in Python instead of chaining .order_by() - a
        # composite (session_id, timestamp) index would otherwise need to be
        # created manually in the Firebase console before this query works.
        from google.cloud.firestore_v1.base_query import FieldFilter

        query = client.collection(settings.firestore_conversations_collection).where(
            filter=FieldFilter("session_id", "==", session_id)
        )
        turns = [doc.to_dict() for doc in query.stream()]
        turns.sort(key=lambda t: t.get("timestamp", ""))
        turns = turns[-limit:]
        return {"available": True, "reason": None, "turns": turns}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"Firestore read failed: {exc}", "turns": []}


def list_conversation_sessions(limit: int = 50) -> dict[str, Any]:
    """List distinct chat sessions (for a "저장된 대화 목록" UI), most recent first.

    Groups all conversation-turn documents by session_id in Python (the
    collection is small enough for this project's scale) rather than
    maintaining a separate sessions index collection.
    """
    try:
        client = get_firestore_client()
    except FirestoreUnavailableError as exc:
        return {"available": False, "reason": str(exc), "sessions": []}

    try:
        docs = [d.to_dict() for d in client.collection(settings.firestore_conversations_collection).stream()]
        by_session: dict[str, list[dict[str, Any]]] = {}
        for doc in docs:
            by_session.setdefault(doc.get("session_id", "default"), []).append(doc)

        sessions = []
        for session_id, turns in by_session.items():
            turns.sort(key=lambda t: t.get("timestamp", ""))
            last = turns[-1]
            sessions.append(
                {
                    "session_id": session_id,
                    "turn_count": len(turns),
                    "last_message": last.get("user_message"),
                    "last_timestamp": last.get("timestamp"),
                }
            )
        sessions.sort(key=lambda s: s.get("last_timestamp") or "", reverse=True)
        return {"available": True, "reason": None, "sessions": sessions[:limit]}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"Firestore read failed: {exc}", "sessions": []}
