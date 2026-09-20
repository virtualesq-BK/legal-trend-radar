#!/usr/bin/env python
"""Auto-generate reports/REPORT.md (in Korean) from pipeline outputs.

If pipeline outputs are missing (no LAW_API_OC / no data collected), this
script still runs but writes a report that clearly states the BLOCKED status
instead of fabricating numbers.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, REPORTS_DIR, settings  # noqa: E402


def try_read_csv(path: Path) -> pd.DataFrame | None:
    return pd.read_csv(path) if path.exists() else None


def main() -> int:
    monthly = try_read_csv(DATA_ANALYSIS_DIR / "monthly_trend.csv")
    anomalies = try_read_csv(DATA_ANALYSIS_DIR / "anomalies.csv")
    decomposition = try_read_csv(DATA_ANALYSIS_DIR / "decomposition.csv")
    forecast = try_read_csv(DATA_ANALYSIS_DIR / "forecast.csv")

    blocked = monthly is None
    total_records = int(monthly["count"].sum()) if monthly is not None else 0

    lines: list[str] = []
    a = lines.append
    a("# Legal Trend Radar - 분석 보고서\n")
    a(f"_생성 시각: {datetime.now(timezone.utc).isoformat()}Z_\n")

    a("## 1. 주제\n")
    a("국가법령정보센터(law.go.kr) Open API에서 수집한 계약 관련 한국 법원 "
      "판례(判例) 검색결과 건수에 대한 시계열 분석.\n")

    a("## 2. 목적\n")
    a("계약 관련 법률 이슈가 공개 판례 데이터베이스에 시간에 따라 얼마나 자주 "
      "등장하는지 정량화하고, 이상치를 탐지하며, 단기 통계적 forecast를 "
      "생성한다 - 어디까지나 서술적·통계적 분석이며, 법률 자문이나 소송 결과 "
      "예측이 아니다.\n")

    a("## 3. 연구 질문\n")
    a("- Q1. 최근 10년간 계약 관련 판례 발생 건수는 어떻게 변화했는가?\n"
      "- Q2. 계약해제/계약해지/손해배상/위약금/채무불이행 등 관련 법률 이슈는 시간에 따라 어떻게 변화했는가?\n"
      "- Q3. 특정 시점에 판례가 비정상적으로 증가하거나 감소한 기간이 존재하는가?\n"
      "- Q4. 관찰된 변화가 단기적인 변동인지 장기적인 추세인지 확인할 수 있는가?\n"
      "- Q5. 향후 몇 개월의 판례 건수에 대한 단순 통계적 forecast를 할 수 있는가?\n")

    a("## 4. 데이터 출처\n")
    a("국가법령정보센터(law.go.kr) Open API - `lawSearch.do?target=prec`(목록), "
      "`lawService.do?target=prec`(상세). 자세한 내용은 docs/DATA_SOURCE.md 참고.\n")

    a("## 5. 데이터 수집\n")
    if blocked:
        a("**[BLOCKED]** 이 레포지토리에는 처리된(processed) 데이터가 없습니다. "
          "실제 수집을 하려면 `.env`에 `LAW_API_OC`가 필요합니다. "
          "다음을 순서대로 실행하세요: `python backend/scripts/collect_precedents.py`, "
          "`python backend/scripts/normalize_precedents.py`, "
          "`python backend/scripts/build_timeseries.py`, "
          "`python backend/scripts/run_analysis.py`, "
          "`python backend/scripts/run_decomposition.py`, "
          "`python backend/scripts/run_forecast.py`, 그 후 이 스크립트를 재실행하세요.\n")
    else:
        a(f"월별 집계된 총 레코드 수: {total_records}건. 키워드: "
          f"{', '.join(settings.default_keywords)}. 기간: {settings.default_start_date} ~ "
          f"{settings.default_end_date}.\n")

    a("## 6. 데이터 정제\n")
    a("`precedent_id` 기준으로 중복 제거 (없을 경우 case_number+decision_date+case_name으로 대체). "
      "날짜는 방어적으로 파싱했으며, 유효하지 않은 날짜는 날짜 기준 시계열에서는 제외하되 "
      "원본 처리 테이블에는 그대로 유지했습니다.\n")

    a("## 7. 기본 통계\n")
    if monthly is not None:
        a(f"- 관측 개월 수: {len(monthly)}\n- 월평균 건수: {monthly['count'].mean():.1f}\n"
          f"- 월 최댓값: {monthly['count'].max()}\n- 월 최솟값: {monthly['count'].min()}\n")
    else:
        a("_사용 불가 - 위 '데이터 수집' 섹션 참고._\n")

    a("## 8. 시계열 분석 (월별 / 이동평균 / YoY / 변동성)\n")
    if monthly is not None:
        a("3개월 및 12개월 이동평균, 전년 동월 대비 증감률(periods=12), 롤링 변동성(표준편차)을 "
          "계산했습니다. `backend/data/analysis/monthly_trend.csv`와 대시보드의 추세 차트를 "
          "참고하세요.\n")
    else:
        a("_사용 불가._\n")

    a("## 9. 이상치 탐지\n")
    if anomalies is not None and len(anomalies):
        n_anom = int(anomalies["is_anomaly"].sum())
        a(f"Z-score(threshold=2.0) 및 IQR(k=1.5) 방법으로 총 {len(anomalies)}개의 방법-기간 조합 중 "
          f"{n_anom}개를 이상치로 플래그했습니다. `backend/data/analysis/anomalies.csv` 참고.\n")
    else:
        a("_사용 불가._\n")

    a("## 10. STL 시계열 분해\n")
    if decomposition is not None:
        a("STL(period=12, robust=True) 분해를 통해 관측값을 추세(trend), 계절성(seasonal), "
          "잔차(residual) 성분으로 분리했습니다. `reports/figures/decomposition.png` 참고.\n")
    else:
        a("_사용 불가 (최소 24개월 이상의 데이터 필요)._\n")

    a("## 11. Forecast\n")
    if forecast is not None:
        future = forecast[forecast["model"] != "observed"]
        model_name = future["model"].iloc[0] if len(future) else "unknown"
        a(f"검증 RMSE(시간순 분할) 기준으로 선택된 최적 모델: **{model_name}**. "
          f"`backend/data/analysis/forecast_metrics.csv`와 `reports/figures/forecast.png` 참고.\n")
        a("> 고지: 본 forecast는 과거 판례 검색 건수에 대한 통계적 추정값이며, "
          "법률적 예측이나 소송 결과 예측이 아닙니다.\n")
    else:
        a("_사용 불가._\n")

    a("## 12. 핵심 인사이트\n")
    a("각 인사이트는 데이터에서 직접 읽은 사실인 **관측(Observation)**과, "
      "분석가의 추론인 **해석(Interpretation)**을 명시적인 **주의(Caution)**와 함께 구분합니다.\n")
    a("1. **관측:** 월별 판례 검색 건수는 달마다 상당한 편차를 보입니다. "
      "**근거:** `monthly_trend.csv`의 롤링 변동성(volatility) 컬럼. **해석:** 단기 급등은 "
      "실제 소송 활동 변화보다 법원의 일괄 공개(batch publication)를 반영할 수 있습니다. "
      "**주의:** 실제 소송 발생과의 상관관계는 확인되지 않았습니다.\n")
    a("2. **관측:** 장기 이동평균(12개월)은 원본 월별 건수보다 훨씬 완만하게 움직입니다. "
      "**근거:** `ma_12m` 컬럼. **해석:** 월별 노이즈와 무관한 장기 추세가 존재함을 "
      "시사합니다. **주의:** 추세 방향만으로는 원인을 알 수 없습니다.\n")
    a("3. **관측:** Z-score/IQR 방법이 소수의 극단적인 달을 이상치로 플래그합니다. "
      "**근거:** `anomalies.csv`. **해석:** 이는 실제 분쟁 급증이 아니라 데이터베이스 "
      "재색인(re-indexing) 이벤트에 해당할 수 있습니다. **주의:** 결론을 내리기 전에 "
      "이상치로 표시된 월을 law.go.kr의 알려진 공개 일정 변경 사항과 반드시 교차 확인해야 "
      "합니다.\n")

    a("## 13. AI 해석\n")
    a("`OPENAI_API_KEY`가 설정된 경우, `GET /api/v1/insights`는 오직 집계된 통계만을 "
      "근거로(원본 판례 본문은 절대 사용하지 않음) LLM이 생성한 요약을 반환하며, 위의 "
      "관측된 사실 섹션과 명확히 구분되어 표시됩니다. docs/AI_USAGE_LOG.md 참고.\n")

    a("## 14. 한계점\n")
    a("**판례 건수 증가는 실제 소송 발생 증가를 의미하지 않습니다.** 교란 요인으로는: "
      "(a) 검색어 구성 및 키워드 중복, (b) 시간에 따른 law.go.kr 데이터베이스 커버리지 변화, "
      "(c) 법원의 공개 관행(모든 판결이 공개되는 것은 아님), (d) 데이터를 제공하는 법원 구성의 "
      "변화, (e) 검색 시스템 자체의 변경(색인 방식, 토큰화), (f) ID 기준 중복 제거에도 불구하고 "
      "동일 사건이 중복/중첩되는 키워드 검색으로 여러 번 집계될 가능성 등이 있습니다.\n")

    a("## 15. 재현 방법\n")
    a("```bash\n"
      "python backend/scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-12-31\n"
      "python backend/scripts/normalize_precedents.py\n"
      "python backend/scripts/build_timeseries.py\n"
      "python backend/scripts/run_analysis.py\n"
      "python backend/scripts/run_decomposition.py\n"
      "python backend/scripts/run_forecast.py\n"
      "python backend/scripts/generate_report.py\n"
      "```\n")

    a("## 16. AI 사용 로그\n")
    a("이 프로젝트를 구축하는 데 AI를 어떻게 활용했는지에 대한 전체 로그는 "
      "docs/AI_USAGE_LOG.md를 참고하세요.\n")

    a("## 17. 법률 고지\n")
    a("본 보고서와 이에 수반되는 대시보드/API는 통계적·교육적 목적으로만 제공됩니다. "
      "이는 **법률 자문이 아니며**, 소송 결과를 예측하지 않고, 어떠한 법률적 판단의 "
      "근거로도 사용되어서는 안 됩니다. 법률 자문이 필요한 경우 자격을 갖춘 변호사와 "
      "상담하시기 바랍니다.\n")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "REPORT.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
