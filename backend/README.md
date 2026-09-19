# Legal Trend Radar - Backend

FastAPI + pandas/statsmodels backend that collects, normalizes, and analyzes
Korean court precedent search-result data from law.go.kr. See the repo-root
README for full setup instructions.

Quick start (PowerShell):
```powershell
cd backend
uv sync --extra dev
uv run pytest -q
uv run uvicorn app.main:app --reload --port 8000
```

If `uv` is unavailable, fall back to:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --port 8000
```
