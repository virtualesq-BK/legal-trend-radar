# Architecture

```
law.go.kr Open API
        |
        v
Collector (backend/scripts/collect_precedents.py)
        |  raw JSON pages
        v
backend/data/raw/*.json
        |
        v
Normalizer (backend/scripts/normalize_precedents.py)
        |  clean, deduped records
        v
backend/data/processed/precedents.{parquet,csv}
        |
        v
Time Series Engine (build_timeseries.py -> timeseries_service.py)
        |  monthly / yearly / keyword / court aggregations
        v
   +----+-----------------+------------------+
   |                      |                  |
   v                      v                  v
Trend/Anomaly       STL Decomposition    Forecast
(run_analysis.py)   (run_decomposition.py) (run_forecast.py)
   |                      |                  |
   +----------+-----------+------------------+
              v
   backend/data/analysis/*.csv + reports/figures/*.png
              |
              v
   AI Interpretation (llm_service.py, optional OPENAI_API_KEY)
              |
              v
        FastAPI (backend/app/main.py)
              |
              v
        Next.js Dashboard (frontend/)
```

## Layering

- **infrastructure/**: talks to the outside world (law.go.kr HTTP client, OpenAI
  client, file-based repositories). Never business logic.
- **services/**: pure(ish) business logic - normalization, aggregation, trend
  math, anomaly detection, STL, forecasting, LLM prompt orchestration.
- **domain/**: shared dataclasses/schemas.
- **api/**: FastAPI routers, translating service/repository errors into clean
  HTTP responses (503 for missing data, never a raw crash).
- **scripts/**: CLI entry points that chain the services together into a
  reproducible pipeline (`Makefile` wires these up as `make collect`,
  `make normalize`, etc).

## Design principles

1. No fake-data fallback anywhere - functions raise `LawApiBlockedError` /
   `DataNotFoundError` with actionable messages instead.
2. Forecast models (ARIMA/SARIMA) are wrapped defensively (`try/except`) so a
   fitting failure degrades to a simpler model rather than crashing the run.
3. Frontend never talks to law.go.kr directly - only to this FastAPI backend,
   via `NEXT_PUBLIC_API_URL`.
