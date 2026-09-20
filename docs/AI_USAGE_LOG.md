# AI 사용 로그

이 로그는 Codyssey AI 응용개발 Final Project 요구사항에 따라, Legal Trend
Radar를 구축하는 데 AI(Claude / Claude Code)를 어떻게 활용했는지 기록합니다.

## Task 1: 아키텍처 설계

**수행 내용:** Claude를 사용해 계층형 백엔드 아키텍처(domain/services/
infrastructure/api), 파이프라인 스크립트 실행 순서(collect -> normalize ->
build_timeseries -> run_analysis -> run_decomposition -> run_forecast ->
generate_report), 프로젝트 사양에 맞춘 레포 구조를 설계했습니다.

**이유:** "외부 API를 호출하는 부분"과 "순수 통계 로직"을 명확히 분리하면
실제 law.go.kr API를 호출하지 않고도 통계 로직을 단위 테스트할 수 있고,
"절대 가짜 데이터를 만들지 않는다"는 원칙을 소수의 지점
(`require_law_api_key`, `DataNotFoundError`)에서만 강제할 수 있습니다.

**검증:** 결과물의 모듈 경계를 직접 검토했고, `pytest`를 통해 네트워크
접근 없이 fixture 데이터만으로 서비스가 독립적으로 테스트 가능함을
확인했습니다.

## Task 2: 코드 생성

**수행 내용:** Claude가 FastAPI 앱, law.go.kr HTTP 클라이언트(재시도/백오프
및 페이지네이션 로직 포함), 정규화/집계/이상치/STL/forecast 서비스, CLI
스크립트, pytest 테스트 스위트(실제 law.go.kr JSON 응답과 동일한 형태의
fixture 포함)를 생성했습니다.

**이유:** "실제 데이터 아니면 명확한 [BLOCKED] 오류, 운영 경로에서는 절대
가짜 데이터 사용 금지" 요구사항에 맞춰, 약 20개 파일에 걸친 전체
파이프라인을 한 번에 일관되게 구현하기 위함입니다.

**검증:** 생성 직후 `uv run pytest`(30/30 통과)와 `uv run ruff check`(클린)를
실행했으며, `LAW_API_OC`를 설정하지 않은 상태로 수집기/정규화 스크립트를
직접 실행해 크래시하거나 데이터를 조작하는 대신 `[BLOCKED]`를 출력하고
비정상 종료 코드를 반환하는지 확인했습니다.

## Task 3: AI 인사이트 생성 (빌드 타임이 아닌 런타임 기능)

**수행 내용:** Claude가 `llm_service.py`의 시스템 프롬프트를 설계해,
런타임에 (`OPENAI_API_KEY`가 설정된 경우에만) 호출되는 OpenAI 요청이
다음을 지키도록 제약했습니다: 관측된 사실과 해석을 구분, 법률 자문 금지,
인과관계 주장 금지, 소송 결과 예측 금지, 숫자 임의 생성 금지, 근거가
부족하면 "증거 불충분"이라고 답변. LLM에는 원본 판례 본문이 아니라 집계된
통계만 전달됩니다.

**이유:** LLM이 실제 수집된 통계에 근거하지 않은, 법률적으로 들리는
주장을 만들어내지 않도록 하기 위함입니다.

**검증:** `generate_insights()`는 "API 키 없음" 경로(가짜 인사이트 대신
명확한 사용 불가 메시지 반환)에 대해 단위 테스트되어 있으며, 프롬프트
내용 자체도 위 5가지 금지 규칙에 맞춰 직접 검토했습니다.

## Task 4: Function Calling + MCP 서버 연동

**수행 내용:** Claude가 `app/services/tools_service.py`에 단일 도구
레지스트리를 설계해, `POST /api/v1/chat`(OpenAI function calling)과
`backend/mcp_server.py`(MCP 서버) 두 채널이 완전히 동일한 함수를 호출하도록
구현했습니다. 이를 통해 GPT가 호출할 수 있는 것과 MCP 클라이언트가 호출할
수 있는 것이 항상 일치하도록 보장합니다.

**이유:** 하나의 데이터 소스에 대해 두 개의 서로 다른 코드 경로를 유지하면
결과가 어긋날 위험이 생기므로, 단일 레지스트리로 통합해 두 채널이 절대
다른 답을 낼 수 없게 했습니다.

**검증:** 실제 OpenAI 호환 게이트웨이에 대해 여러 질문("이상치가 몇 개
감지됐어?" 등)으로 실제 도구 호출 흐름을 검증했고, MCP 서버는
`list_tools()`/`call_tool()`을 직접 호출해 6~7개 도구가 정상 등록·실행됨을
확인했습니다.

## Task 5: Firestore 연동 (분석 데이터 + 대화 기록 + CRUD)

**수행 내용:** Claude가 `app/infrastructure/firestore_client.py`와
`app/services/firestore_service.py`를 설계해 `FIREBASE_CREDENTIALS_JSON`
환경변수(서비스 계정 키 JSON, 코드에 하드코딩하지 않음)로 Firestore를
초기화하고, `data`(분석 스냅샷 + 사용자 CRUD 레코드)와 `conversations`
(채팅 기록) 두 컬렉션을 설계했습니다.

**이유:** 사용자가 직접 관리하는 데이터와 대화 기록을 영구 저장하면서도,
Firestore가 설정되지 않았거나 오류가 나도 핵심 기능(파이프라인/API/채팅)이
절대 깨지지 않도록 하기 위함입니다.

**검증:** 실제 Firebase 프로젝트에 대해 CRUD 전체 생명주기(생성→목록→수정→
삭제)를 실행해 결과를 재조회로 확인했고, 대화 기록 조회 시 Firestore
복합 인덱스 요구 문제를 발견해 단일 필드 필터 + Python 정렬 방식으로
수정했습니다. 41/41 pytest 통과(가짜 Firestore 클라이언트로 컬렉션 구조
검증 포함).
