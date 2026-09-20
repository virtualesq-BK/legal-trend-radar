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


def call_openai_with_tools(
    system_prompt: str,
    user_message: str,
    tools: list[dict[str, Any]],
    tool_executor,
    max_rounds: int = 4,
) -> dict[str, Any]:
    """Run an OpenAI function-calling loop.

    `tool_executor(name, arguments) -> dict` actually runs the requested tool
    (see app/services/tools_service.py) - this function only orchestrates the
    back-and-forth with the model. Returns the final assistant answer plus a
    transcript of every tool call made, so callers/UI can show *which* tool
    was invoked and *why* (the model's own tool_calls are the evidence trail).
    """
    if not settings.openai_api_key:
        raise LlmUnavailableError("OPENAI_API_KEY not set")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise LlmUnavailableError(
            "openai package not installed; run `uv add openai` to enable chat/tool calling"
        ) from exc

    client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url or None)
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message},
    ]
    tool_calls_made: list[dict[str, Any]] = []

    for _ in range(max_rounds):
        last_exc: Exception | None = None
        resp = None
        # Same graceful-degradation strategy as call_openai_json: some
        # gateways/models reject temperature or tool_choice="auto" explicitly.
        for kwargs in ({"tool_choice": "auto", "temperature": 0.1}, {"tool_choice": "auto"}, {}):
            try:
                resp = client.chat.completions.create(
                    model=settings.openai_model, messages=messages, tools=tools, **kwargs
                )
                break
            except Exception as exc:  # noqa: BLE001 - provider-agnostic fallback chain
                last_exc = exc
                continue
        if resp is None:
            raise LlmUnavailableError(f"OpenAI-compatible tool call failed: {last_exc}") from last_exc

        message = resp.choices[0].message
        requested = getattr(message, "tool_calls", None)
        if not requested:
            return {"answer": message.content or "", "tool_calls": tool_calls_made}

        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in requested
                ],
            }
        )
        for tc in requested:
            name = tc.function.name
            try:
                arguments = json.loads(tc.function.arguments or "{}")
            except ValueError:
                arguments = {}
            try:
                result = tool_executor(name, arguments)
                error = None
            except Exception as exc:  # noqa: BLE001 - report tool failure back to the model
                result = None
                error = str(exc)
            tool_calls_made.append({"name": name, "arguments": arguments, "error": error})
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result if error is None else {"error": error}, ensure_ascii=False),
                }
            )

    raise LlmUnavailableError("Tool-calling loop did not converge within max_rounds")
