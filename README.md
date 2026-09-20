# Legal Trend Radar

Codyssey AI 응용개발 Final Project. 국가법령정보센터(law.go.kr) Open API에서
**실제** 한국 법원 판례(判例) 검색결과 데이터를 수집하고, 정제한 뒤 월별/연별
시계열을 구축하고, 이상치를 탐지하며, STL 시계열 분해와 ARIMA/SARIMA
Forecast를 수행하고, 선택적으로 AI 기반 구조화 인사이트를 생성하여
FastAPI 백엔드와 Next.js 대시보드로 제공합니다.

> **법률 자문 아님 고지:** 본 프로젝트는 공개된 판례 *검색결과 건수*에 대한
> 통계적·시계열 분석을 제공합니다. 이는 **법률 자문이 아니며**, 소송 결과를
> **예측하지 않습니다**. 법률적 판단이 필요한 경우 반드시 변호사와
> 상담하십시오.

## 배포 (Live Demo)

- **프론트엔드 (Vercel):** https://legal-trend-radar.vercel.app/dashboard
- **백엔드 (Render):** https://legal-trend-radar-backend.onrender.com
  (API 문서: `/docs`, 헬스체크: `/health`)
- 소스: https://github.com/virtualesq-BK/legal-trend-radar

두 서비스 모두 실제 수집·정제된 판례 데이터(3,133건)로 서빙됩니다. Render
무료 플랜은 영구 디스크가 없어 백엔드 배포 시 파이프라인을 다시 돌릴 수
없으므로, 이미 실제 API로 수집·검증된 `backend/data/processed/`와
`backend/data/analysis/` 결과물을 레포에 커밋해 배포와 함께 제공합니다
(원본 raw JSON 덤프는 재현성 확인용으로만 필요하므로 계속 gitignore 처리).
Render 무료 인스턴스는 일정 시간 요청이 없으면 슬립 상태가 되어 첫 요청
응답이 몇십 초 정도 걸릴 수 있습니다.

## 아키텍처

전체 파이프라인 다이어그램은 `docs/ARCHITECTURE.md`를 참고하세요:
```
law.go.kr -> Collector -> Raw JSON -> Normalizer -> Parquet ->
Time Series Engine -> Trend/Anomaly/STL -> Forecast -> AI Interpretation ->
FastAPI -> Next.js Dashboard
```

## 기술 스택

- **Backend:** Python 3.11+, FastAPI, Pydantic, httpx, pandas, numpy, scipy,
  statsmodels, scikit-learn, python-dotenv, matplotlib, seaborn, pytest, ruff.
  의존성 관리는 [`uv`](https://github.com/astral-sh/uv)를 사용합니다 (`uv`가
  없는 환경에서는 아래 안내대로 `pip` + `venv`로 대체 가능).
- **Frontend:** Next.js (App Router) + TypeScript + Tailwind CSS + Recharts.

## 데이터 출처

국가법령정보센터 Open API (`lawSearch.do` / `lawService.do`, `target=prec`).
전체 파라미터 레퍼런스는 `docs/DATA_SOURCE.md`를 참고하세요.

**본 프로젝트는 API Key를 절대 하드코딩하지 않으며, 실패 시에도 가짜
데이터로 대체하지 않습니다.** API Key가 없으면 모든 스크립트/엔드포인트는
크래시하거나 숫자를 임의로 만들어내는 대신 명확한 `[BLOCKED]` 메시지를
출력/반환합니다.

알아두면 좋은 구현 디테일 하나: `lawSearch.do`/`lawService.do`는
**charset 헤더 없이 EUC-KR로 인코딩된 바이트**를 응답으로 돌려줍니다.
httpx의 기본 `response.json()`은 UTF-8을 가정하기 때문에 오류 없이
조용히 모든 한글 필드를 깨진 문자(mojibake)로 만들어 버립니다. 그래서
`app/infrastructure/law_api_client.py`는 JSON을 파싱하기 전에 원본 응답
바이트를 먼저 EUC-KR로 (실패 시 UTF-8로) 직접 디코딩합니다. 이 API에서
한글이 깨져 나온다면 십중팔구 이 문제입니다.

## 환경 변수

레포 루트의 `.env.example`을 `.env`로 복사한 뒤 값을 채워주세요:

| 변수 | 필수 여부 | 설명 |
|---|---|---|
| `LAW_API_OC` (별칭 `LAW_OC`) | 실제 데이터 수집에 **필수** | law.go.kr Open API OC id (https://open.law.go.kr 에서 "사용자 인증키 신청"으로 발급). 두 이름 중 아무거나 사용 가능 — `app/config.py`가 pydantic `AliasChoices`로 두 이름 모두 허용하므로 기존 `LAW_OC` 값을 굳이 바꿀 필요가 없습니다. 둘 다 설정된 경우 값이 비어있지 않은 쪽이 우선 적용되지만, 빈 `LAW_API_OC=` 줄이 있으면 (값이 비어 있어도) 먼저 검사되어 채워진 `LAW_OC`보다 "우선"해버리므로, 실제로 사용하지 않는 변수는 아예 `.env`에서 지우는 것이 안전합니다. |
| `OPENAI_API_KEY` | 선택 | `GET /api/v1/insights` (AI 기반 구조화 인사이트)를 활성화합니다. 없으면 해당 엔드포인트는 가짜 인사이트 대신 "AI insights unavailable" 응답을 명확히 반환합니다. |
| `OPENAI_MODEL` | 선택 (기본값 `gpt-4o-mini`) | 모델명. OpenAI가 아닌 게이트웨이를 사용한다면 먼저 `client.models.list()`로 지원 모델을 확인하세요 — 제공자/게이트웨이마다 모델명이 다릅니다. |
| `OPENAI_BASE_URL` | 선택 | `api.openai.com`이 아닌 OpenAI 호환 프록시/게이트웨이를 사용할 때만 설정합니다. `llm_client.py`는 게이트웨이가 `response_format`이나 기본값이 아닌 `temperature`를 거부하는 경우 (일부 게이트웨이/최신 `gpt-5*` 계열 모델 등) 파라미터를 줄여가며 재시도하는 방식으로 우아하게 대응합니다. |
| `BACKEND_URL` / `NEXT_PUBLIC_API_URL` | 기본값 있음 | 프론트엔드가 FastAPI 백엔드를 찾는 위치. 프론트엔드는 law.go.kr을 직접 호출하지 않습니다. |
| `DEFAULT_START_DATE` / `DEFAULT_END_DATE` | 기본값 있음 | `--start-date`/`--end-date`를 지정하지 않았을 때 `collect_precedents.py`가 사용하는 기본 수집 기간 (`2016-01-01` ~ `2026-12-31`). |
| `FORECAST_HORIZON` | 기본값 있음 (`6`) | `run_forecast.py`가 예측하는 개월 수. |
| `RUN_INTEGRATION_TESTS` | 기본값 있음 (`false`) | `true`로 설정하면 테스트 스위트에서 law.go.kr에 대한 최소한의 실제 네트워크 통합 테스트를 허용합니다. |
| `FIREBASE_CREDENTIALS_JSON` | 선택 | Firestore 연동(분석 데이터/대화 기록 저장)을 활성화합니다. Firebase 콘솔에서 발급받은 서비스 계정 키 JSON 파일의 **전체 내용을 한 줄로** 붙여넣으세요. 키 파일 자체는 절대 레포에 커밋하지 않습니다. 비워두면 Firestore 없이도 전체 기능이 정상 동작합니다. |

## 설치

### Backend (PowerShell)

`uv` 사용 (권장, 이 프로젝트를 빌드/검증할 때 사용한 방식):
```powershell
cd backend
uv sync --extra dev
```

`uv` 없이 (대체 방법 - 별도의 `requirements.txt`는 없으며 `pyproject.toml`이
유일한 의존성 정의 소스이므로 `pip install -e ".[dev]"`가 동일한 의존성
목록을 읽습니다):
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Frontend (PowerShell)
```powershell
cd frontend
npm install
copy .env.local.example .env.local
```

## 파이프라인 실행 (CLI)

Bash:
```bash
python backend/scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-12-31
python backend/scripts/normalize_precedents.py
python backend/scripts/build_timeseries.py
python backend/scripts/run_analysis.py
python backend/scripts/run_decomposition.py
python backend/scripts/run_forecast.py
python backend/scripts/generate_report.py
```

PowerShell (with `uv`):
```powershell
cd backend
uv run python scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-12-31
uv run python scripts/normalize_precedents.py
uv run python scripts/build_timeseries.py
uv run python scripts/run_analysis.py
uv run python scripts/run_decomposition.py
uv run python scripts/run_forecast.py
uv run python scripts/generate_report.py
```

또는 간단히: `make all` (make 호환 셸 필요; Windows에서는 Git Bash나
WSL을 사용하거나 위 명령어를 하나씩 개별 실행하세요).

### 실제 데이터 수집 현황

실제 law.go.kr API에 설정된 키로 정상적으로 수집을 완료했습니다. 현재
파이프라인 결과:

- 계약, 계약해제, 계약해지, 손해배상, 위약금, 채무불이행 6개 키워드
  전체에 걸쳐 **3,133건**의 고유한 판례 검색결과 레코드를 수집했으며,
  기간은 **2016-01-08 ~ 2026-08-13** (128개월)로, 최소 요구 건수(100건),
  분석 질문(3개 이상), 10년 이상 데이터 확보 목표를 모두 충분히
  충족합니다.
- 정제 후 유효하고 파싱 가능한 판결일자 비율은 **100.0%**입니다.
- `reports/figures/`에 필수 PNG 6종(월별/연별/키워드별 추세, 이상치
  타임라인, STL 분해, Forecast)이 모두 생성되어 있습니다.
- Forecast 모델 비교 결과 (시간순 분할, 수치가 낮을수록 우수):
  `naive` RMSE 16.87, `moving_average` RMSE 14.37, `sarima` RMSE 10.95,
  **`arima` RMSE 9.49 (최종 선택 모델)**.
- `reports/REPORT.md`는 자리표시자가 아닌 실제 수치로 완전히 생성되어
  있습니다.
- `OPENAI_API_KEY`가 설정되어 있으면 `GET /api/v1/insights`가 실제
  AI 생성 구조화 인사이트를 반환합니다 (아래 참고); 이 레포의 `.env`에는
  Codyssey OpenAI 호환 게이트웨이용 키가 설정되어 있습니다.

API Key 없이 이 레포를 clone하거나 `backend/data/{raw,processed,analysis}/`가
비워지면, 모든 스크립트/API 엔드포인트는 자리표시자 데이터를 조용히 쓰는
대신 명확한 `[BLOCKED]` 메시지를 출력/반환하는 상태로 돌아갑니다 — 이는
모든 수집 경로가 반드시 거치는 단일 지점인 `app/config.py`의
`require_law_api_key()`에서 강제됩니다.

전체 파이프라인 재실행 (PowerShell):
```powershell
cd backend
uv run python scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-09-20 --display 100 --max-pages 20
uv run python scripts/normalize_precedents.py
uv run python scripts/build_timeseries.py
uv run python scripts/run_analysis.py
uv run python scripts/run_decomposition.py
uv run python scripts/run_forecast.py
uv run python scripts/generate_report.py
```

## Backend 실행

```powershell
cd backend
uv run uvicorn app.main:app --reload --port 8000
```
API 문서: http://localhost:8000/docs · 레퍼런스: `docs/API.md`

## Frontend 실행

```powershell
cd frontend
npm run dev
```
대시보드: http://localhost:3000/dashboard

## 보너스 과제

### 1) AI 도구 호출 (Function Calling) + 멀티채널 연동

**설계 원칙:** GPT는 통계 수치를 직접 알지 못합니다. 질문에 답하려면 반드시
아래 "도구(tool)" 중 하나 이상을 호출해서 실제 파이프라인 데이터를 가져와야
하며, 이는 GPT function calling과 MCP 두 채널 모두에서 **동일한 코드**를
호출하도록 만들어 두 채널이 서로 다른 답을 낼 수 없게 했습니다.

```
backend/app/services/tools_service.py   ← 도구 스키마 + 함수 (단일 소스)
        ├── get_monthly_trend(limit)
        ├── get_yearly_trend()
        ├── get_keyword_trend(keyword?)
        ├── get_anomalies(only_flagged)
        ├── get_forecast()
        └── get_statistics()
              │
              ├── POST /api/v1/chat  (OpenAI function calling, app/services/chat_service.py)
              └── mcp_server.py      (MCP Server, stdio transport)
```

**호출 흐름 (예: "최근 이상치가 언제 발생했어?"):**
1. 사용자가 `/api/v1/chat`에 자연어 질문을 보냄 (원시 데이터는 전혀 함께
   보내지 않음, 도구 스키마만 GPT에 전달).
2. GPT가 질문을 분석해 어떤 도구가 필요한지 스스로 판단 → 이 예시에서는
   `get_anomalies(only_flagged=true)` 호출을 요청.
3. 백엔드가 실제로 `tools_service.tool_get_anomalies()`를 실행해 (이미
   수집·검증된 실데이터 기준) 결과를 GPT에 다시 전달.
4. GPT가 도구 결과만 근거로 최종 답변을 생성 (숫자 임의 생성 금지, 근거 없는
   주장 금지 — `chat_service.py`의 시스템 프롬프트로 강제).
5. API 응답에 `tool_calls` 배열로 **어떤 도구를, 어떤 인자로, 성공/실패
   여부와 함께** 호출했는지 그대로 노출 → 대시보드의 "AI에게 데이터
   질문하기" 패널(`ChatPanel.tsx`)에서 답변 아래에 실제 호출 로그로
   표시됩니다.

실제 호출 예시 (2026-09-20 로컬 검증):
```
POST /api/v1/chat  {"message": "이 데이터에서 이상치가 몇 개 감지됐고, 가장 최근 이상치는 언제야?"}
→ tool_calls: [{"name": "get_anomalies", "arguments": {"only_flagged": true}}]
→ answer: "...가장 최근 이상치는 2026-08이며... (출처: get_anomalies 결과)"
```

**두 번째 채널 (MCP Server):** `backend/mcp_server.py`가 동일한 6개 도구를
[MCP](https://modelcontextprotocol.io) 서버로 노출합니다. Claude Desktop 등
MCP 클라이언트에서 아래처럼 등록하면 GPT 채팅 없이도 동일한 함수를 직접 호출할
수 있습니다:
```json
{
  "mcpServers": {
    "legal-trend-radar": {
      "command": "uv",
      "args": ["run", "--directory", "<repo>/backend", "python", "mcp_server.py"]
    }
  }
}
```
로컬에서 도구 목록/호출을 직접 검증하려면:
```powershell
cd backend
uv run python -c "import mcp_server, asyncio; print(asyncio.run(mcp_server.mcp.list_tools()))"
uv run python -c "import mcp_server, asyncio; print(asyncio.run(mcp_server.mcp.call_tool('get_statistics', {})))"
```

### 2) 인사이트·UX 고도화

- **통계 API 확장:** `GET /api/v1/data/statistics` 신규 엔드포인트로 중앙값,
  표준편차, 전체 기간 증감률(growth rate), 이상치 비율, 최고/최저 월 등
  기존 `/precedents/summary`에 없던 지표를 제공합니다. 대시보드의
  "상세 통계" 패널(`StatisticsPanel.tsx`)에서 표시됩니다.
- **신규 시각화:** `YoYChart.tsx` — 기존에 데이터에는 있었지만 별도
  그래프가 없었던 전년 동월 대비 증감률(YoY %)을 막대그래프로 시각화
  (양수/음수를 색으로 구분).
- **데이터 내보내기:** `GET /api/v1/export/monthly?format=csv|json`로 월별
  추이 데이터를 CSV/JSON으로 다운로드할 수 있습니다. 대시보드 헤더의
  "⬇ CSV 다운로드"/"⬇ JSON 다운로드" 버튼에서 바로 사용 가능합니다.
- **다크 모드 토글:** 헤더의 🌙/☀️ 버튼으로 라이트/다크 테마를 전환하며,
  `localStorage`에 저장되어 다음 방문 시에도 유지됩니다 (Tailwind v4의
  `@custom-variant dark` + `.dark` 클래스 전략, `layout.tsx`의 초기화
  스크립트로 첫 렌더링 시 깜빡임 방지).

### 3) Firestore (Firebase) 연동

Google Cloud Firestore를 사용해 분석 데이터와 대화 기록을 영구 저장합니다.

**서비스 계정 키 관리:** 키 파일을 레포에 커밋하지 않고, Firebase 콘솔에서
발급받은 서비스 계정 키 JSON 전체 내용을 `FIREBASE_CREDENTIALS_JSON`
환경변수 하나에 문자열로 저장합니다 (`app/config.py`가 `.env`에서 읽음).
`app/infrastructure/firestore_client.py`가 이 값을 `json.loads()`로 파싱해
`firebase_admin.credentials.Certificate()`에 전달하는 방식이라 서버리스
배포 환경(Render/Vercel 등)에도 파일 없이 배포할 수 있습니다. 값이 없거나
잘못돼도 앱은 크래시하지 않고 해당 기능만 "not configured"로 비활성화됩니다
(`OPENAI_API_KEY`와 동일한 선택적 연동 원칙).

**컬렉션 구조:**

| 컬렉션 | 문서 ID | 용도 | 쓰는 곳 |
|---|---|---|---|
| `data` | 분석 실행 시각(`collected_at`) | 파이프라인 실행 결과 스냅샷(전체 판례 수, 월별/연별 추이, 통계, forecast 지표)을 타임스탬프별로 누적 저장 — 재실행해도 기존 기록을 덮어쓰지 않음 | `backend/scripts/sync_firestore.py` → `firestore_service.save_analysis_snapshot()` |
| `conversations` | 자동 생성 UUID | `/api/v1/chat` 한 턴(질문, 호출된 도구, 최종 답변, `session_id`, 타임스탬프)을 매번 기록 | `chat_service.run_chat()` → `firestore_service.save_conversation_turn()` (best-effort — Firestore 오류가 채팅 응답 자체를 막지 않음) |

조회 API: `GET /api/v1/firestore/status` (연동 상태), `GET
/api/v1/conversations?session_id=...` (해당 세션의 대화 기록 조회).

**동기화 실행:**
```powershell
cd backend
uv run python scripts/sync_firestore.py
```
또는 `make sync-firestore`.

## 구현 노트 (실제 데이터 실행 중 수정한 사항)

실제 API로 실행하는 과정에서 몇 가지 문제가 발견되어 아래와 같이
코드베이스에 수정 반영했습니다 (재발견을 방지하기 위해 기록):

1. **EUC-KR 응답 디코딩.** 위 "데이터 출처" 항목 참고 — `law_api_client.py`는
   httpx의 UTF-8 기본값을 신뢰하는 대신 원본 응답 바이트를 명시적으로
   디코딩합니다.
2. **`LAW_OC` vs `LAW_API_OC`.** 두 이름 모두 허용됩니다 (`app/config.py`).
   다만 alias 해석 로직이 값이 비어 있어도 존재하는 첫 번째 키를 선택하기
   때문에, `.env`에 *비어있는* `LAW_API_OC=` 줄이 있으면 값이 채워진
   `LAW_OC=...`보다 여전히 우선합니다. 실제로 사용하는 변수 하나만
   `.env`에 남겨두세요.
3. **NaN은 유효한 JSON이 아닙니다.** 이동평균/전년동월대비(YoY)는 시계열
   초반 몇 개 기간에서는 (충분한 과거 데이터가 없어) `NaN`이 됩니다.
   pandas의 `DataFrame.to_dict()`는 이를 float `NaN` 그대로 유지하는데,
   이는 FastAPI의 JSON 렌더러를 크래시시킵니다
   (`ValueError: Out of range float values are not JSON compliant`).
   `app/api/dependencies.to_records()`에서 `.to_dict()` *이후에*
   `NaN`/`Inf`를 `None`으로 정제하는 방식으로 수정했습니다 (`.to_dict()`
   전에 `DataFrame.where()`로 처리하면 동작하지 않습니다 — pandas가 float
   컬럼에 대입된 `None`을 조용히 다시 `NaN`으로 되돌려버리기 때문입니다).
4. **OpenAI 호환 게이트웨이마다 지원하는 파라미터가 다릅니다.** 일부는
   `response_format={"type": "json_object"}`를 거부하고, 일부(예: 최신
   `gpt-5*` 계열 모델)는 기본값이 아닌 `temperature`를 거부합니다.
   `llm_client.py`는 파라미터 조합을 단계적으로 줄여가며 재시도하고,
   응답에서 마크다운 코드펜스를 제거한 뒤 JSON을 파싱하므로, 엄격한
   OpenAI든 관대한 프록시든 OpenAI 비호환 게이트웨이든 특정 제공자를
   가정하지 않고 동작합니다.
5. **`FIREBASE_CREDENTIALS_JSON`은 반드시 한 줄이어야 합니다.** `.env`
   파서(`python-dotenv`)는 값이 줄바꿈 없이 한 줄에 있어야 읽습니다.
   Firebase 콘솔에서 받은 키 JSON 파일을 줄바꿈이 살아있는 상태로 그대로
   붙여넣으면 `{` 한 글자만 읽히고 나머지 줄은 조용히 무시됩니다(에러 없이
   `Firestore not configured`로만 보임 — 원인 파악이 어려움). 붙여넣기 전에
   반드시 JSON을 한 줄로 압축(minify)하세요, 예:
   `python -c "import json,sys; print(json.dumps(json.load(open('key.json'))))"`.
   (참고: `private_key` 필드 내부의 `\n`은 이미 JSON 문자열 이스케이프이므로
   문제가 되지 않습니다 — 문제는 오직 최상위 JSON 객체 `{...}` 자체가 여러
   줄에 걸쳐 있을 때입니다.)
6. **Firestore 복합 인덱스 없이 조회하도록 설계.** 처음에는
   `list_conversation_history()`가 `.where("session_id", ...).order_by("timestamp")`를
   함께 사용했는데, 이는 Firestore 콘솔에서 수동으로 복합 인덱스를 생성해야만
   동작합니다(`FAILED_PRECONDITION: The query requires an index`). 별도
   설정 없이 바로 동작하도록 `session_id`만으로 필터링(단일 필드는 자동
   인덱싱됨)한 뒤 결과를 Python에서 정렬하도록 수정했습니다.

## 테스트

```powershell
cd backend
uv run pytest -q
uv run ruff check .
```

테스트는 실제 law.go.kr JSON 응답과 동일한 형태의 작은 합성(fixture)
데이터를 사용하며 기본적으로 네트워크를 호출하지 않습니다. 실제
`LAW_API_OC`가 있는 경우 `.env`에서 `RUN_INTEGRATION_TESTS=true`로
설정하면 최소한의 실제 통합 테스트(`query=계약, display=1`)를 추가로
허용합니다.

## Docker

```bash
docker compose up --build
```
Backend는 :8000, Frontend는 :3000. 레포 루트에 `.env`가 필요합니다.

## AI 사용 내역

`docs/AI_USAGE_LOG.md`에 AI(Claude / Claude Code)를 이 프로젝트 설계·구현에
어떻게 활용했는지, 그리고 런타임 AI 인사이트 기능(`GET /api/v1/insights`)이
법률 자문, 인과관계 주장, 숫자 임의 생성을 피하도록 어떻게 제약되어
있는지 기록되어 있습니다.

## 한계점

판례 검색결과 건수의 변화가 실제 소송 발생 건수의 변화와 **동일한 것은
아닙니다**. 검색어 구성, law.go.kr 데이터베이스 커버리지, 법원별 공개
관행, 시간에 따른 법원 구성 변화, 검색 시스템/색인 방식 변경 등이 교란
요인으로 작용할 수 있습니다. 전체 논의는 `generate_report.py`가 자동
생성하는 `reports/REPORT.md`의 "Limitations" 섹션을 참고하세요.

LSTM 기반 Forecast는 이번 빌드에서 명시적으로 **범위 밖**입니다;
안정성과 재현성을 고려하여 ARIMA/SARIMA를 채택했으며, LSTM은 보고서에
후속 과제로 명시되어 있습니다.

## 법률 자문 아님 고지

본 프로젝트와 그 API, 대시보드는 통계적·교육적 목적으로만 제공됩니다.
여기 담긴 어떠한 내용도 법률 자문에 해당하지 않으며, 어떠한 법적 분쟁의
결과도 예측하지 않습니다. 법률 문제는 반드시 자격을 갖춘 변호사와
상담하시기 바랍니다.
