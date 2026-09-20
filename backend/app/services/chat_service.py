"""GPT chat endpoint with function calling ("tool use") over real pipeline data.

The model NEVER receives raw data up front - it must explicitly call one of
the tools in TOOL_SPECS to fetch numbers, and every tool call is logged and
returned to the caller so the UI/README can show *which* tool was invoked and
*why* (the model's stated need, inferred from the user's question).
"""
from __future__ import annotations

from typing import Any

from app.infrastructure.llm_client import LlmUnavailableError, call_openai_with_tools
from app.services.tools_service import TOOL_FUNCTIONS, TOOL_SPECS

SYSTEM_PROMPT = """You are a data-analysis assistant for the Legal Trend Radar dashboard,
which analyzes SEARCH RESULT counts for Korean court precedents (not litigation counts).

You do not know any statistics yourself. To answer a question, you MUST call one or more of
the provided tools to fetch real numbers - never guess or invent a number.

Rules:
1. Never give legal advice or comment on legal merits.
2. Never claim correlation implies causation, and never predict litigation outcomes.
3. Every numeric claim in your answer must come from a tool result.
4. If the available tools cannot answer the question, say so explicitly instead of guessing.
5. Keep answers concise and cite the concrete numbers you used.
"""


def run_chat(user_message: str) -> dict[str, Any]:
    def executor(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        fn = TOOL_FUNCTIONS.get(name)
        if fn is None:
            raise ValueError(f"Unknown tool: {name}")
        return fn(**arguments)

    try:
        result = call_openai_with_tools(SYSTEM_PROMPT, user_message, TOOL_SPECS, executor)
        return {"available": True, "answer": result["answer"], "tool_calls": result["tool_calls"], "reason": None}
    except LlmUnavailableError as exc:
        return {"available": False, "answer": None, "tool_calls": [], "reason": str(exc)}
    except Exception as exc:  # never crash the API on LLM/tool failure
        return {"available": False, "answer": None, "tool_calls": [], "reason": f"chat failed: {exc}"}
