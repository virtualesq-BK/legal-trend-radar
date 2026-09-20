"""CRUD API for user-managed (date, value, memo) data records.

Stored in Firestore's `data` collection alongside pipeline snapshots (see
app/services/firestore_service.py for the collection design). Requires
FIREBASE_CREDENTIALS_JSON; every endpoint returns a clear 503 [BLOCKED]
response if Firestore isn't configured, never a fabricated result.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.firestore_service import (
    create_data_record,
    delete_data_record,
    list_data_records,
    update_data_record,
)

router = APIRouter()


class DataRecordIn(BaseModel):
    date: str
    value: float
    memo: str | None = None


class DataRecordPatch(BaseModel):
    date: str | None = None
    value: float | None = None
    memo: str | None = None


@router.get("/api/v1/data/records")
def list_records():
    result = list_data_records()
    if not result["available"]:
        raise HTTPException(status_code=503, detail=f"[BLOCKED] {result['reason']}")
    return result["records"]


@router.post("/api/v1/data/records", status_code=201)
def create_record(payload: DataRecordIn):
    result = create_data_record(payload.date, payload.value, payload.memo)
    if not result["saved"]:
        raise HTTPException(status_code=503, detail=f"[BLOCKED] {result['reason']}")
    return result["record"]


@router.put("/api/v1/data/records/{record_id}")
def update_record(record_id: str, payload: DataRecordPatch):
    result = update_data_record(record_id, payload.date, payload.value, payload.memo)
    if not result["saved"]:
        status = 404 if "not found" in (result["reason"] or "") else 503
        detail = result["reason"] if status == 404 else f"[BLOCKED] {result['reason']}"
        raise HTTPException(status_code=status, detail=detail)
    return {"updated": True, "id": record_id}


@router.delete("/api/v1/data/records/{record_id}")
def delete_record(record_id: str):
    result = delete_data_record(record_id)
    if not result["saved"]:
        status = 404 if "not found" in (result["reason"] or "") else 503
        detail = result["reason"] if status == 404 else f"[BLOCKED] {result['reason']}"
        raise HTTPException(status_code=status, detail=detail)
    return {"deleted": True, "id": record_id}
