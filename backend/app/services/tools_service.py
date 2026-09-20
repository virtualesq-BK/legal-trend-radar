"""Tool ("function calling") registry shared by both integration channels:

1. `POST /api/v1/chat` - an OpenAI-compatible chat endpoint where the LLM
   decides which of these tools to call based on the user's question.
2. `backend/mcp_server.py` - an MCP server exposing the exact same
   functions, so any MCP client (Claude Desktop, another agent, etc.) can
   call them directly without going through the chat endpoint at all.

Keeping ONE registry that both channels wrap guarantees they can never drift:
whatever GPT can do via /api/v1/chat, an MCP client can do identically, and
both ultimately just call the same read-only repository/service functions
the REST API itself uses - so tool calls can only ever return real, already
-validated data, never invented numbers.
"""
from __future__ import annotations

from typing import Any, Callable

from app.infrastructure.repositories import (
    load_anomalies,
    load_forecast,
    load_keywords,
    load_monthly,
    load_yearly,
)
from app.services.firestore_service import list_data_records
from app.services.statistics_service import compute_statistics


def tool_get_monthly_trend(limit: int = 12) -> dict[str, Any]:
    """Return the most recent `limit` months of precedent search-result counts."""
    df = load_monthly()
    tail = df.tail(max(1, min(limit, len(df))))
    return {"rows": tail.to_dict(orient="records")}


def tool_get_yearly_trend() -> dict[str, Any]:
    """Return yearly precedent search-result counts."""
    df = load_yearly()
    return {"rows": df.to_dict(orient="records")}


def tool_get_keyword_trend(keyword: str | None = None) -> dict[str, Any]:
    """Return monthly counts broken down by search keyword, optionally filtered to one keyword."""
    df = load_keywords()
    if keyword:
        df = df[df["search_keyword"] == keyword]
    return {"rows": df.to_dict(orient="records")}


def tool_get_anomalies(only_flagged: bool = True) -> dict[str, Any]:
    """Return detected anomalies (z-score and IQR methods)."""
    df = load_anomalies()
    if only_flagged:
        df = df[df["is_anomaly"]]
    return {"rows": df.to_dict(orient="records")}


def tool_get_forecast() -> dict[str, Any]:
    """Return the ARIMA/SARIMA forecast points with confidence intervals."""
    df = load_forecast()
    return {
        "disclaimer": (
            "Statistical extrapolation only - NOT a legal or litigation prediction."
        ),
        "rows": df.to_dict(orient="records"),
    }


def tool_get_statistics() -> dict[str, Any]:
    """Return enriched summary statistics (median, growth rate, anomaly rate, peak/trough month)."""
    return compute_statistics(load_monthly(), load_anomalies())


def tool_get_saved_data_summary() -> dict[str, Any]:
    """Return a summary of the user's manually saved (date, value, memo) records in Firestore.

    Use this when the user asks about "저장된 데이터"/"내가 추가한 데이터" - the
    records they created through the Data Management (CRUD) screen - as
    opposed to the automatically collected precedent trend data.
    """
    result = list_data_records()
    if not result["available"]:
        return {"available": False, "reason": result["reason"], "records": []}
    records = result["records"]
    values = [r["value"] for r in records if isinstance(r.get("value"), (int, float))]
    return {
        "available": True,
        "count": len(records),
        "date_range": {
            "start": records[0]["date"] if records else None,
            "end": records[-1]["date"] if records else None,
        },
        "value_sum": sum(values) if values else None,
        "value_mean": (sum(values) / len(values)) if values else None,
        "records": records,
    }


# OpenAI function-calling / MCP tool schemas. Kept intentionally small and
# strictly typed so the model can only ask for exactly the data it needs.
TOOL_SPECS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_monthly_trend",
            "description": tool_get_monthly_trend.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "How many of the most recent months to return (default 12).",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_yearly_trend",
            "description": tool_get_yearly_trend.__doc__,
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_keyword_trend",
            "description": tool_get_keyword_trend.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "One of 계약/계약해제/계약해지/손해배상/위약금/채무불이행. Omit for all keywords.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_anomalies",
            "description": tool_get_anomalies.__doc__,
            "parameters": {
                "type": "object",
                "properties": {
                    "only_flagged": {
                        "type": "boolean",
                        "description": "If true (default), return only months flagged as anomalous.",
                    }
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_forecast",
            "description": tool_get_forecast.__doc__,
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_statistics",
            "description": tool_get_statistics.__doc__,
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_saved_data_summary",
            "description": tool_get_saved_data_summary.__doc__,
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

TOOL_FUNCTIONS: dict[str, Callable[..., dict[str, Any]]] = {
    "get_monthly_trend": tool_get_monthly_trend,
    "get_yearly_trend": tool_get_yearly_trend,
    "get_keyword_trend": tool_get_keyword_trend,
    "get_anomalies": tool_get_anomalies,
    "get_forecast": tool_get_forecast,
    "get_statistics": tool_get_statistics,
    "get_saved_data_summary": tool_get_saved_data_summary,
}
