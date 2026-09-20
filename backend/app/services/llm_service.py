"""Generate structured AI insights from precomputed statistics ONLY.

Raw legal text is never sent to the LLM - only aggregated numeric stats.
The system prompt enforces: distinguish observed fact from interpretation,
no legal advice, no causation from correlation, no litigation-outcome
prediction, no invented numbers, and "insufficient evidence" when appropriate.
"""
from __future__ import annotations

from typing import Any

from app.config import settings
from app.infrastructure.llm_client import LlmUnavailableError, call_openai_json

SYSTEM_PROMPT = """You are a cautious data-analysis assistant summarizing statistics about
Korean court precedent SEARCH RESULT counts (not litigation counts) over time.

Rules you MUST follow:
1. Clearly separate "observed facts" (numbers given to you) from "interpretation" (your reasoning).
2. Never give legal advice or comment on legal merits.
3. Never claim correlation implies causation.
4. Never predict litigation outcomes or legal risk for any party.
5. Every numeric claim you make must be traceable to a number in the supplied stats. Never invent numbers.
6. If the data is insufficient to support a claim, say "증거가 불충분합니다" (insufficient evidence) instead of guessing.
7. Remember: precedent count changes may reflect database/search artifacts, not real-world litigation volume.
8. Write every string value in the JSON response in Korean (한국어), since this is displayed on a Korean-language dashboard. Numbers/dates may stay in their original format.

Respond ONLY with a JSON object of this exact shape (all string values in Korean):
{"summary": str, "observations": [str], "interpretations": [str], "hypotheses": [str], "limitations": [str]}
"""

UNAVAILABLE_REASON = "AI insights unavailable - set OPENAI_API_KEY in .env to enable this feature."


def generate_insights(stats: dict[str, Any]) -> dict[str, Any]:
    if not settings.openai_api_key:
        return {
            "available": False,
            "summary": UNAVAILABLE_REASON,
            "observations": [],
            "interpretations": [],
            "hypotheses": [],
            "limitations": [],
            "reason": UNAVAILABLE_REASON,
        }
    try:
        result = call_openai_json(SYSTEM_PROMPT, stats)
        return {
            "available": True,
            "summary": result.get("summary", ""),
            "observations": result.get("observations", []),
            "interpretations": result.get("interpretations", []),
            "hypotheses": result.get("hypotheses", []),
            "limitations": result.get("limitations", []),
            "reason": None,
        }
    except LlmUnavailableError as exc:
        return {
            "available": False,
            "summary": str(exc),
            "observations": [],
            "interpretations": [],
            "hypotheses": [],
            "limitations": [],
            "reason": str(exc),
        }
    except Exception as exc:  # never crash the API on LLM failure
        return {
            "available": False,
            "summary": f"AI insight generation failed: {exc}",
            "observations": [],
            "interpretations": [],
            "hypotheses": [],
            "limitations": [],
            "reason": str(exc),
        }
