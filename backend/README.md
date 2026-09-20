# Legal Trend Radar - Backend

law.go.kr에서 한국 법원 판례 검색결과 데이터를 수집·정규화·분석하는
FastAPI + pandas/statsmodels 백엔드입니다. 전체 설정 방법은 레포 루트의
README를 참고하세요.

빠른 시작 (PowerShell):
```powershell
cd backend
uv sync --extra dev
uv run pytest -q
uv run uvicorn app.main:app --reload --port 8000
```

`uv`를 사용할 수 없는 경우:
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest -q
uvicorn app.main:app --reload --port 8000
```
