from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.infrastructure.firestore_client import firestore_status
from app.services.firestore_service import list_conversation_history

router = APIRouter()


@router.get("/api/v1/firestore/status")
def status():
    """Whether Firestore is configured and reachable (never raises)."""
    return firestore_status()


@router.get("/api/v1/conversations")
def conversations(session_id: str = Query("default")):
    """Read back a chat session's history from the `conversations` collection."""
    result = list_conversation_history(session_id)
    if not result["available"]:
        raise HTTPException(status_code=503, detail=result["reason"])
    return result
