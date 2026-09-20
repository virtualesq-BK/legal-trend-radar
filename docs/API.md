# Backend API Reference

Base URL: `http://localhost:8000` (or `BACKEND_URL` / `NEXT_PUBLIC_API_URL`)

All endpoints return JSON. When the underlying pipeline data has not been
generated yet, endpoints return **HTTP 503** with a body like:
```json
{ "detail": "[BLOCKED] Required data file not found: ... Action: run `...`." }
```
This is intentional - the API never returns fabricated data or crashes with
a raw 500 when data is missing.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Liveness + whether `LAW_API_OC` / `OPENAI_API_KEY` are configured |
| GET | `/api/v1/precedents/summary` | Total records, date range, keywords, courts, sufficiency vs. minimum (100) |
| GET | `/api/v1/trends/monthly` | Monthly counts + 3M/12M moving average + YoY + volatility |
| GET | `/api/v1/trends/yearly` | Yearly counts |
| GET | `/api/v1/trends/keywords` | Monthly counts broken down by search keyword |
| GET | `/api/v1/trends/courts` | Counts by court type |
| GET | `/api/v1/anomalies` | Z-score + IQR anomaly flags per month |
| GET | `/api/v1/decomposition` | STL trend/seasonal/residual components |
| GET | `/api/v1/forecast` | Naive/MA/ARIMA/SARIMA comparison result + forecast points + disclaimer |
| GET | `/api/v1/insights` | AI-generated structured insight (or "unavailable" message if no `OPENAI_API_KEY`) |
| GET | `/api/v1/metadata` | Data source name, default keywords/date range, legal disclaimer |
| POST | `/api/v1/collect` | Guidance response pointing to the CLI collector (long-running collection is intentionally not run synchronously over HTTP) |
| GET | `/api/v1/data/statistics` | Enriched stats: median, std dev, full-period growth rate, anomaly rate, peak/trough month |
| GET | `/api/v1/export/monthly?format=csv\|json` | Download the monthly trend table as a file (`Content-Disposition: attachment`) |
| POST | `/api/v1/chat` | Body `{"message": "...", "session_id": "default"}`. GPT function-calling endpoint - the model calls one or more tools from `app/services/tools_service.py` to fetch real data before answering. Returns `{"answer", "tool_calls": [{"name","arguments","error"}]}`. Requires `OPENAI_API_KEY`; returns 503 `[BLOCKED]` otherwise. Each turn is also best-effort persisted to Firestore's `conversations` collection if configured. See README "보너스 과제" for the full call-flow walkthrough. |
| GET | `/api/v1/firestore/status` | Whether Firestore (`FIREBASE_CREDENTIALS_JSON`) is configured and reachable |
| GET | `/api/v1/conversations/sessions` | List distinct chat sessions (session_id, turn_count, last_message, last_timestamp), most recent first |
| GET | `/api/v1/conversations?session_id=...` | Read back a chat session's history from Firestore's `conversations` collection (503 `[BLOCKED]` if Firestore isn't configured) |
| GET | `/api/v1/data/records` | List all user-managed `(date, value, memo)` records from Firestore's `data` collection |
| POST | `/api/v1/data/records` | Body `{"date","value","memo"}`. Create a record; returns 201 + the created record with its `id` |
| PUT | `/api/v1/data/records/{id}` | Body `{"date"?,"value"?,"memo"?}`. Patch a record (404 if not found) |
| DELETE | `/api/v1/data/records/{id}` | Delete a record (404 if not found) |

Interactive OpenAPI docs are available at `/docs` when the server is running.

## MCP Server (second integration channel)

`backend/mcp_server.py` exposes the exact same 7 tools as `/api/v1/chat` via
the [Model Context Protocol](https://modelcontextprotocol.io), so any MCP
client (Claude Desktop, another agent) can call them directly:

```powershell
cd backend
uv run python mcp_server.py   # stdio transport
```

Both channels call the same functions in `app/services/tools_service.py`, so
they can never disagree about what a tool returns.
