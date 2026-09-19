"""Thin OpenAI client wrapper. Only used when OPENAI_API_KEY is set."""
from __future__ import annotations

import json
import re
from typing import Any

from app.config import settings


class LlmUnavailableError(RuntimeError):
    pass


def _extract_json(text: str) -> dict[str, Any]:
    """Parse a JSON object out of a model response.

    Some OpenAI-compatible gateways don't support `response_format:
    json_object` and/or wrap the JSON in a markdown code fence - handle both.
    """
    text = text.strip()
    fenced = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fenced:
        text = fenced.group(1)
    return json.loads(text)


def call_openai_json(system_prompt: str, user_payload: dict[str, Any]) -> dict[str, Any]:
    if not settings.openai_api_key:
        raise LlmUnavailableError("OPENAI_API_KEY not set")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LlmUnavailableError(
            "openai package not installed; run `uv add openai` to enable AI insights"
        ) from exc

    client = OpenAI(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url or None,
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
    ]
    # Different OpenAI-compatible gateways/models support different subsets of
    # parameters (e.g. some reject response_format, newer "gpt-5*" models
    # reject a non-default temperature) - degrade gracefully instead of
    # failing outright just because of an unsupported request option.
    attempts = [
        {"response_format": {"type": "json_object"}, "temperature": 0.2},
        {"temperature": 0.2},
        {"response_format": {"type": "json_object"}},
        {},
    ]
    last_exc: Exception | None = None
    resp = None
    for kwargs in attempts:
        try:
            resp = client.chat.completions.create(
                model=settings.openai_model, messages=messages, **kwargs
            )
            break
        except Exception as exc:  # noqa: BLE001 - provider-agnostic fallback chain
            last_exc = exc
            continue
    if resp is None:
        raise LlmUnavailableError(f"OpenAI-compatible call failed: {last_exc}") from last_exc
    content = resp.choices[0].message.content or "{}"
    try:
        return _extract_json(content)
    except ValueError as exc:
        raise LlmUnavailableError(
            f"Model response was not valid JSON: {content[:200]}"
        ) from exc
