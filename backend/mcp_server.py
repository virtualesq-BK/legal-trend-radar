#!/usr/bin/env python
"""MCP server exposing Legal Trend Radar's analysis tools to any MCP client
(Claude Desktop, another agent, etc.) - a second, independent integration
channel for the exact same functions used by `POST /api/v1/chat`.

This deliberately does NOT reimplement any analysis logic: every tool below
just calls into `app.services.tools_service`, the same registry the FastAPI
chat endpoint uses. That means an MCP client and GPT function-calling can
never disagree about what a tool returns - they call the identical code path
against the same real, already-collected precedent data.

Run (stdio transport, for e.g. Claude Desktop's mcpServers config):
    uv run python mcp_server.py

Example Claude Desktop config entry:
    "legal-trend-radar": {
      "command": "uv",
      "args": ["run", "--directory", "<path-to>/backend", "python", "mcp_server.py"]
    }
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# NOTE: mcp>=2.0 renamed FastMCP to MCPServer; the decorator/run() API is
# otherwise unchanged from the widely-documented FastMCP examples.
from mcp.server.mcpserver import MCPServer  # noqa: E402

from app.services.tools_service import (  # noqa: E402
    tool_get_anomalies,
    tool_get_forecast,
    tool_get_keyword_trend,
    tool_get_monthly_trend,
    tool_get_saved_data_summary,
    tool_get_statistics,
    tool_get_yearly_trend,
)

mcp = MCPServer("legal-trend-radar")


@mcp.tool()
def get_monthly_trend(limit: int = 12) -> dict:
    """Return the most recent `limit` months of precedent search-result counts."""
    return tool_get_monthly_trend(limit=limit)


@mcp.tool()
def get_yearly_trend() -> dict:
    """Return yearly precedent search-result counts."""
    return tool_get_yearly_trend()


@mcp.tool()
def get_keyword_trend(keyword: str | None = None) -> dict:
    """Return monthly counts broken down by search keyword, optionally filtered to one keyword."""
    return tool_get_keyword_trend(keyword=keyword)


@mcp.tool()
def get_anomalies(only_flagged: bool = True) -> dict:
    """Return detected anomalies (z-score and IQR methods)."""
    return tool_get_anomalies(only_flagged=only_flagged)


@mcp.tool()
def get_forecast() -> dict:
    """Return the ARIMA/SARIMA forecast points with confidence intervals. NOT legal advice."""
    return tool_get_forecast()


@mcp.tool()
def get_statistics() -> dict:
    """Return enriched summary statistics (median, growth rate, anomaly rate, peak/trough month)."""
    return tool_get_statistics()


@mcp.tool()
def get_saved_data_summary() -> dict:
    """Return a summary of the user's manually saved (date, value, memo) records in Firestore."""
    return tool_get_saved_data_summary()


if __name__ == "__main__":
    mcp.run(transport="stdio")
