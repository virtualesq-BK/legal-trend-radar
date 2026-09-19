.PHONY: install collect normalize analyze decompose forecast report test lint backend frontend all

install:
	cd backend && uv sync --extra dev
	cd frontend && npm install

collect:
	cd backend && uv run python scripts/collect_precedents.py

normalize:
	cd backend && uv run python scripts/normalize_precedents.py
	cd backend && uv run python scripts/build_timeseries.py

analyze:
	cd backend && uv run python scripts/run_analysis.py

decompose:
	cd backend && uv run python scripts/run_decomposition.py

forecast:
	cd backend && uv run python scripts/run_forecast.py

report:
	cd backend && uv run python scripts/generate_report.py

test:
	cd backend && uv run pytest -q

lint:
	cd backend && uv run ruff check .

backend:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm run dev

all: collect normalize analyze decompose forecast report
