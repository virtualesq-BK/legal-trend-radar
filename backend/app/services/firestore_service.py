"""Firestore persistence for Legal Trend Radar.

Collection design:

- `data`         : one document per analysis snapshot (a full pipeline run's
                    output: precedent summary + monthly/yearly trend +
                    enriched statistics + forecast metrics). Document ID is
                    the run's `collected_at` timestamp, so re-running the
                    pipeline creates a new, timestamped snapshot rather than
                    silently overwriting history.
- `conversations`: one document per chat turn (question + tool calls +
                    answer), grouped by `session_id` so a UI could later
                    reconstruct a full conversation thread.

Both are optional/best-effort: if Firestore isn't configured
(`FIREBASE_CREDENTIALS_JSON` unset) or a write fails, callers get back a
clear {"saved": False, "reason": ...} instead of an exception - persistence
here is an add-on, never a blocker for the core pipeline/API/chat.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from app.config import settings
from app.infrastructure.firestore_client import FirestoreUnavailableError, get_firestore_client


def save_analysis_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Write one analysis snapshot to the `data` collection.

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
            {**snapshot, "saved_at": datetime.now(timezone.utc).isoformat()}
        )
        return {"saved": True, "reason": None, "doc_id": doc_id}
    except Exception as exc:  # noqa: BLE001 - never let a Firestore hiccup break the caller
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
        query = (
            client.collection(settings.firestore_conversations_collection)
            .where("session_id", "==", session_id)
            .order_by("timestamp", direction="DESCENDING")
            .limit(limit)
        )
        turns = [doc.to_dict() for doc in query.stream()]
        turns.reverse()
        return {"available": True, "reason": None, "turns": turns}
    except Exception as exc:  # noqa: BLE001
        return {"available": False, "reason": f"Firestore read failed: {exc}", "turns": []}
