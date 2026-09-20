# Backend API 레퍼런스

Base URL: `http://localhost:8000` (또는 `BACKEND_URL` / `NEXT_PUBLIC_API_URL`)

모든 엔드포인트는 JSON을 반환합니다. 파이프라인 데이터가 아직 생성되지
않은 경우 다음과 같은 형태로 **HTTP 503**을 반환합니다:
```json
{ "detail": "[BLOCKED] Required data file not found: ... Action: run `...`." }
```
이는 의도된 동작입니다 - 데이터가 없을 때 API가 가짜 데이터를 반환하거나
원시 500 오류로 크래시하지 않습니다.

| Method | Path | 설명 |
|---|---|---|
| GET | `/health` | 생존 확인 + `LAW_API_OC` / `OPENAI_API_KEY` / Firestore 설정 여부 |
| GET | `/api/v1/precedents/summary` | 총 레코드 수, 기간, 키워드, 법원, 최소 요구 건수(100) 대비 충족 여부 |
| GET | `/api/v1/trends/monthly` | 월별 건수 + 3M/12M 이동평균 + YoY + 변동성 |
| GET | `/api/v1/trends/yearly` | 연별 건수 |
| GET | `/api/v1/trends/keywords` | 검색 키워드별 월별 건수 |
| GET | `/api/v1/trends/courts` | 법원 유형별 건수 |
| GET | `/api/v1/anomalies` | 월별 Z-score + IQR 이상치 플래그 |
| GET | `/api/v1/decomposition` | STL 추세/계절성/잔차 성분 |
| GET | `/api/v1/forecast` | Naive/MA/ARIMA/SARIMA 비교 결과 + forecast 포인트 + 고지문 |
| GET | `/api/v1/insights` | AI 생성 구조화 인사이트 (`OPENAI_API_KEY` 없으면 "unavailable" 메시지) |
| GET | `/api/v1/metadata` | 데이터 출처명, 기본 키워드/기간, 법률 고지문 |
| POST | `/api/v1/collect` | CLI 수집기 안내 응답 (장시간 소요되는 수집은 의도적으로 HTTP 동기 실행하지 않음) |
| GET | `/api/v1/data/statistics` | 확장 통계: 중앙값, 표준편차, 전체기간 증감률, 이상치 비율, 최고/최저 월 |
| GET | `/api/v1/export/monthly?format=csv\|json` | 월별 추이 테이블을 파일로 다운로드 (`Content-Disposition: attachment`) |
| POST | `/api/v1/chat` | Body `{"message": "...", "session_id": "default"}`. GPT function-calling 엔드포인트 - 모델이 `app/services/tools_service.py`의 도구를 하나 이상 호출해 실제 데이터를 가져온 뒤 답변합니다. `{"answer", "tool_calls": [{"name","arguments","error"}]}` 반환. `OPENAI_API_KEY` 필요, 없으면 503 `[BLOCKED]`. 매 턴은 설정된 경우 Firestore `conversations` 컬렉션에 best-effort로 저장됩니다. 전체 호출 흐름은 README "보너스 과제" 참고. |
| GET | `/api/v1/firestore/status` | Firestore(`FIREBASE_CREDENTIALS_JSON`) 설정 및 연결 가능 여부 |
| GET | `/api/v1/conversations/sessions` | 저장된 채팅 세션 목록 (session_id, turn_count, last_message, last_timestamp), 최신순 |
| GET | `/api/v1/conversations?session_id=...` | Firestore `conversations` 컬렉션에서 특정 세션의 대화 기록 조회 (Firestore 미설정 시 503 `[BLOCKED]`) |
| GET | `/api/v1/data/records` | Firestore `data` 컬렉션의 사용자 관리 `(date, value, memo)` 레코드 전체 목록 |
| POST | `/api/v1/data/records` | Body `{"date","value","memo"}`. 레코드 생성; 201 + 생성된 레코드(`id` 포함) 반환 |
| PUT | `/api/v1/data/records/{id}` | Body `{"date"?,"value"?,"memo"?}`. 레코드 수정 (없으면 404) |
| DELETE | `/api/v1/data/records/{id}` | 레코드 삭제 (없으면 404) |

서버 실행 중에는 `/docs`에서 대화형 OpenAPI 문서를 확인할 수 있습니다.

## MCP 서버 (두 번째 연동 채널)

`backend/mcp_server.py`는 `/api/v1/chat`과 동일한 7개 도구를
[MCP(Model Context Protocol)](https://modelcontextprotocol.io)로 노출해,
어떤 MCP 클라이언트(Claude Desktop, 다른 에이전트 등)든 직접 호출할 수
있게 합니다:

```powershell
cd backend
uv run python mcp_server.py   # stdio transport
```

두 채널 모두 `app/services/tools_service.py`의 동일한 함수를 호출하므로,
도구 결과가 서로 어긋날 수 없습니다.
