# 아키텍처

```
law.go.kr Open API
        |
        v
수집기 (Collector) (backend/scripts/collect_precedents.py)
        |  원본 JSON 페이지
        v
backend/data/raw/*.json
        |
        v
정규화기 (Normalizer) (backend/scripts/normalize_precedents.py)
        |  정제·중복제거된 레코드
        v
backend/data/processed/precedents.{parquet,csv}
        |
        v
시계열 엔진 (Time Series Engine) (build_timeseries.py -> timeseries_service.py)
        |  월별 / 연별 / 키워드별 / 법원별 집계
        v
   +----+-----------------+------------------+
   |                      |                  |
   v                      v                  v
추세/이상치            STL 분해            Forecast
(run_analysis.py)   (run_decomposition.py) (run_forecast.py)
   |                      |                  |
   +----------+-----------+------------------+
              v
   backend/data/analysis/*.csv + reports/figures/*.png
              |
              v
   AI 해석 (llm_service.py, 선택사항 - OPENAI_API_KEY 필요)
              |
              v
        FastAPI (backend/app/main.py)
              |
              v
        Next.js 대시보드 (frontend/)
```

## 계층 구조

- **infrastructure/**: 외부 세계와 통신하는 계층 (law.go.kr HTTP 클라이언트,
  OpenAI 클라이언트, Firestore 클라이언트, 파일 기반 리포지토리). 비즈니스
  로직을 포함하지 않습니다.
- **services/**: (거의) 순수한 비즈니스 로직 - 정규화, 집계, 추세 계산,
  이상치 탐지, STL, forecast, LLM 프롬프트 오케스트레이션, Firestore
  영속화, 도구(tool) 레지스트리.
- **domain/**: 공유 dataclass/스키마.
- **api/**: FastAPI 라우터. 서비스/리포지토리 오류를 깔끔한 HTTP 응답으로
  변환합니다 (데이터 누락 시 503, 원시 크래시는 절대 없음).
- **scripts/**: 여러 서비스를 재현 가능한 파이프라인으로 연결하는 CLI
  진입점 (`Makefile`이 `make collect`, `make normalize` 등으로 연결).

## 설계 원칙

1. 어디에도 가짜 데이터 대체 로직이 없습니다 - 함수는 실패 시 실행 가능한
   조치가 담긴 메시지와 함께 `LawApiBlockedError` / `DataNotFoundError`를
   발생시킵니다.
2. Forecast 모델(ARIMA/SARIMA)은 방어적으로 감싸져 있어(`try/except`)
   적합(fitting) 실패 시 전체 실행이 크래시하는 대신 더 단순한 모델로
   대체됩니다.
3. 프론트엔드는 law.go.kr을 직접 호출하지 않으며, 오직 `NEXT_PUBLIC_API_URL`을
   통해 이 FastAPI 백엔드만 호출합니다.
4. Firestore(선택 연동)도 동일한 원칙을 따릅니다 - `FIREBASE_CREDENTIALS_JSON`이
   없거나 잘못돼도 해당 기능만 "미설정" 상태로 비활성화될 뿐, 앱 전체가
   크래시하지 않습니다.
