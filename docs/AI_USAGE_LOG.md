# AI Usage Log

This log records how AI assistance (Claude / Claude Code) was used to build
Legal Trend Radar, as required for this Codyssey AI Final Project.

## Task 1: Architecture design

**What was done:** Claude was used to design the layered backend architecture
(domain/services/infrastructure/api), the pipeline script ordering (collect ->
normalize -> build_timeseries -> run_analysis -> run_decomposition ->
run_forecast -> generate_report), and the repo layout matching the project
spec.

**Why:** A clear separation between "things that call external APIs" and
"pure statistical logic" makes it possible to unit-test the statistics
without ever hitting the real law.go.kr API, and makes the "never fabricate
data" rule enforceable at a small number of choke points
(`require_law_api_key`, `DataNotFoundError`).

**Validation:** Reviewed the resulting module boundaries manually; confirmed
via `pytest` that services can be tested in isolation with fixture data with
no network access.

## Task 2: Code generation

**What was done:** Claude generated the FastAPI app, the law.go.kr HTTP
client (with retry/backoff and pagination math), the normalization/aggregation/
anomaly/STL/forecast services, the CLI scripts, and the pytest test suite
(fixtures shaped like real law.go.kr JSON responses).

**Why:** To implement the full pipeline correctly and consistently with the
"real data or clear [BLOCKED] error, never mock data in production paths"
requirement, across ~20 files, in a single coherent pass.

**Validation:** `uv run pytest` (30/30 passing) and `uv run ruff check` (clean)
were run after generation; the collector and normalizer scripts were manually
executed with no `LAW_API_OC` set to confirm they print `[BLOCKED]` and exit
non-zero instead of crashing or fabricating data.

## Task 3: AI insight generation (runtime feature, not build-time)

**What was done:** Claude designed the `llm_service.py` system prompt that
constrains a downstream OpenAI call (used at runtime, only if
`OPENAI_API_KEY` is set) to: separate observed fact from interpretation,
avoid legal advice, avoid causal claims, avoid litigation-outcome prediction,
never invent numbers, and say "insufficient evidence" when appropriate. Only
aggregated statistics (never raw case text) are sent to the LLM.

**Why:** The project must not let an LLM produce legal-sounding claims not
grounded in the actual collected statistics.

**Validation:** `generate_insights()` is unit-tested for the "no API key"
path (returns a clear unavailable message, not fake insights); the prompt
content itself was manually reviewed against the five prohibition rules
above.
