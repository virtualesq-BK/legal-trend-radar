from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.chat_service import run_chat

router = APIRouter()


class ChatRequest(BaseModel):
    message: str


@router.post("/api/v1/chat")
def chat(req: ChatRequest):
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=503,
            detail="[BLOCKED] OPENAI_API_KEY not set. Set it in .env to enable /api/v1/chat.",
        )
    result = run_chat(req.message)
    if not result["available"]:
        raise HTTPException(status_code=502, detail=result["reason"])
    return result
