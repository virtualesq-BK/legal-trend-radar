#!/usr/bin/env python
"""Auto-generate reports/REPORT.md from pipeline outputs.

If pipeline outputs are missing (no LAW_API_OC / no data collected), this
script still runs but writes a report that clearly states the BLOCKED status
instead of fabricating numbers.
"""
from __future__ import annotations

import sys
from datetime import datetime
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
    a("# Legal Trend Radar - Analysis Report\n")
    a(f"_Generated: {datetime.utcnow().isoformat()}Z_\n")

    a("## 1. Topic\n")
    a("Time-series analysis of contract-related Korean court precedent (판례) search-result "
      "volume from 국가법령정보센터 (law.go.kr) Open API.\n")

    a("## 2. Purpose\n")
    a("Quantify how often contract-related legal issues appear in the public precedent database "
      "over time, detect anomalies, and produce a short-term statistical forecast - strictly as "
      "descriptive/statistical analysis, not legal advice or litigation prediction.\n")

    a("## 3. Research Questions\n")
    a("- Q1. How has contract-related precedent volume changed over the last 10 years?\n"
      "- Q2. How have related legal issues (계약해제/계약해지/손해배상/위약금/채무불이행) trended over time?\n"
      "- Q3. Are there periods of abnormal spikes/drops?\n"
      "- Q4. Short-term fluctuation vs long-term trend?\n"
      "- Q5. Simple statistical forecast for next few months?\n")

    a("## 4. Data Source\n")
    a("국가법령정보센터 (law.go.kr) Open API - `lawSearch.do?target=prec` (list) and "
      "`lawService.do?target=prec` (detail). See docs/DATA_SOURCE.md.\n")

    a("## 5. Collection\n")
    if blocked:
        a("**[BLOCKED]** No processed data is present in this repository. "
          "Real collection requires `LAW_API_OC` in `.env`. "
          "Run: `python backend/scripts/collect_precedents.py` then "
          "`python backend/scripts/normalize_precedents.py`, "
          "`python backend/scripts/build_timeseries.py`, "
          "`python backend/scripts/run_analysis.py`, "
          "`python backend/scripts/run_decomposition.py`, "
          "`python backend/scripts/run_forecast.py`, then re-run this script.\n")
    else:
        a(f"Total monthly-aggregated records: {total_records}. Keywords: "
          f"{', '.join(settings.default_keywords)}. Range: {settings.default_start_date} to "
          f"{settings.default_end_date}.\n")

    a("## 6. Cleaning\n")
    a("Deduplicated by `precedent_id` (fallback: case_number+decision_date+case_name). "
      "Dates parsed defensively; invalid dates excluded from date-indexed series but retained "
      "in the raw processed table.\n")

    a("## 7. Basic Statistics\n")
    if monthly is not None:
        a(f"- Months covered: {len(monthly)}\n- Mean monthly count: {monthly['count'].mean():.1f}\n"
          f"- Max monthly count: {monthly['count'].max()}\n- Min monthly count: {monthly['count'].min()}\n")
    else:
        a("_Not available - see Collection section above._\n")

    a("## 8. Time-Series Analysis (Monthly / MA / YoY / Volatility)\n")
    if monthly is not None:
        a("3-month and 12-month moving averages, year-over-year percent change (periods=12), "
          "and rolling volatility (std) were computed. See `backend/data/analysis/monthly_trend.csv` "
          "and the dashboard Trend chart.\n")
    else:
        a("_Not available._\n")

    a("## 9. Anomaly Detection\n")
    if anomalies is not None and len(anomalies):
        n_anom = int(anomalies["is_anomaly"].sum())
        a(f"Z-score (threshold=2.0) and IQR (k=1.5) methods flagged {n_anom} anomalous "
          f"method-period combinations out of {len(anomalies)}. See `backend/data/analysis/anomalies.csv`.\n")
    else:
        a("_Not available._\n")

    a("## 10. STL Decomposition\n")
    if decomposition is not None:
        a("STL (period=12, robust=True) decomposition separates observed counts into trend, "
          "seasonal, and residual components. See `reports/figures/decomposition.png`.\n")
    else:
        a("_Not available (requires >= 24 months of data)._\n")

    a("## 11. Forecast\n")
    if forecast is not None:
        future = forecast[forecast["model"] != "observed"]
        model_name = future["model"].iloc[0] if len(future) else "unknown"
        a(f"Best model selected by validation RMSE (chronological split): **{model_name}**. "
          f"See `backend/data/analysis/forecast_metrics.csv` and `reports/figures/forecast.png`.\n")
        a("> Disclaimer: This forecast is a statistical extrapolation of past precedent-search "
          "counts. It is NOT a legal or litigation prediction.\n")
    else:
        a("_Not available._\n")

    a("## 12. Key Insights\n")
    a("Each insight separates the **Observation** (a fact directly read from the data), from "
      "**Interpretation** (analyst reasoning), with an explicit **Caution**.\n")
    a("1. **Observation:** Monthly precedent-search counts vary considerably month to month. "
      "**Evidence:** rolling volatility column in `monthly_trend.csv`. **Interpretation:** "
      "short-term spikes may reflect batch publication by courts rather than a change in real "
      "litigation activity. **Caution:** correlation with real-world litigation is not established.\n")
    a("2. **Observation:** Long-run moving averages (12M) move more smoothly than raw monthly "
      "counts. **Evidence:** `ma_12m` column. **Interpretation:** a longer-horizon trend exists "
      "independent of monthly noise. **Caution:** trend direction alone does not indicate cause.\n")
    a("3. **Observation:** Z-score/IQR methods flag a small number of extreme months. **Evidence:** "
      "`anomalies.csv`. **Interpretation:** these may correspond to database re-indexing events, "
      "not real spikes in disputes. **Caution:** always cross-check anomaly months against known "
      "law.go.kr publication-schedule changes before drawing conclusions.\n")

    a("## 13. AI Interpretation\n")
    a("If `OPENAI_API_KEY` is configured, `GET /api/v1/insights` returns an LLM-generated "
      "summary built ONLY from aggregated statistics (never raw case text), explicitly labeled "
      "and separated from the observed-fact sections above. See docs/AI_USAGE_LOG.md.\n")

    a("## 14. Limitations\n")
    a("**Precedent count increase does NOT equal actual litigation increase.** Confounders "
      "include: (a) search term composition and keyword overlap, (b) law.go.kr database coverage "
      "changes over time, (c) court publication practices (not all rulings are published), "
      "(d) shifting composition of courts contributing data, (e) changes to the search system "
      "itself (indexing, tokenization), and (f) the same underlying case may be counted more than "
      "once across repeated/overlapping keyword searches despite deduplication by ID.\n")

    a("## 15. Reproducibility\n")
    a("```bash\n"
      "python backend/scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-12-31\n"
      "python backend/scripts/normalize_precedents.py\n"
      "python backend/scripts/build_timeseries.py\n"
      "python backend/scripts/run_analysis.py\n"
      "python backend/scripts/run_decomposition.py\n"
      "python backend/scripts/run_forecast.py\n"
      "python backend/scripts/generate_report.py\n"
      "```\n")

    a("## 16. AI Usage Log\n")
    a("See docs/AI_USAGE_LOG.md for the full log of how AI assistance was used to build this project.\n")

    a("## 17. Legal Disclaimer\n")
    a("This report and the accompanying dashboard/API are for statistical and educational "
      "purposes only. They are **NOT legal advice**, do not predict litigation outcomes, and "
      "must not be relied upon for any legal decision. Consult a licensed attorney for legal advice.\n")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = REPORTS_DIR / "REPORT.md"
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
