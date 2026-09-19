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

Interactive OpenAPI docs are available at `/docs` when the server is running.
