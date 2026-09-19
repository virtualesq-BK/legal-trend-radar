# Legal Trend Radar - Analysis Report

_Generated: 2026-09-19T21:47:34.704942Z_

## 1. Topic

Time-series analysis of contract-related Korean court precedent (판례) search-result volume from 국가법령정보센터 (law.go.kr) Open API.

## 2. Purpose

Quantify how often contract-related legal issues appear in the public precedent database over time, detect anomalies, and produce a short-term statistical forecast - strictly as descriptive/statistical analysis, not legal advice or litigation prediction.

## 3. Research Questions

- Q1. How has contract-related precedent volume changed over the last 10 years?
- Q2. How have related legal issues (계약해제/계약해지/손해배상/위약금/채무불이행) trended over time?
- Q3. Are there periods of abnormal spikes/drops?
- Q4. Short-term fluctuation vs long-term trend?
- Q5. Simple statistical forecast for next few months?

## 4. Data Source

국가법령정보센터 (law.go.kr) Open API - `lawSearch.do?target=prec` (list) and `lawService.do?target=prec` (detail). See docs/DATA_SOURCE.md.

## 5. Collection

Total monthly-aggregated records: 3133. Keywords: 계약, 계약해제, 계약해지, 손해배상, 위약금, 채무불이행. Range: 2016-01-01 to 2026-12-31.

## 6. Cleaning

Deduplicated by `precedent_id` (fallback: case_number+decision_date+case_name). Dates parsed defensively; invalid dates excluded from date-indexed series but retained in the raw processed table.

## 7. Basic Statistics

- Months covered: 128
- Mean monthly count: 24.5
- Max monthly count: 40
- Min monthly count: 2

## 8. Time-Series Analysis (Monthly / MA / YoY / Volatility)

3-month and 12-month moving averages, year-over-year percent change (periods=12), and rolling volatility (std) were computed. See `backend/data/analysis/monthly_trend.csv` and the dashboard Trend chart.

## 9. Anomaly Detection

Z-score (threshold=2.0) and IQR (k=1.5) methods flagged 7 anomalous method-period combinations out of 256. See `backend/data/analysis/anomalies.csv`.

## 10. STL Decomposition

STL (period=12, robust=True) decomposition separates observed counts into trend, seasonal, and residual components. See `reports/figures/decomposition.png`.

## 11. Forecast

Best model selected by validation RMSE (chronological split): **arima**. See `backend/data/analysis/forecast_metrics.csv` and `reports/figures/forecast.png`.

> Disclaimer: This forecast is a statistical extrapolation of past precedent-search counts. It is NOT a legal or litigation prediction.

## 12. Key Insights

Each insight separates the **Observation** (a fact directly read from the data), from **Interpretation** (analyst reasoning), with an explicit **Caution**.

1. **Observation:** Monthly precedent-search counts vary considerably month to month. **Evidence:** rolling volatility column in `monthly_trend.csv`. **Interpretation:** short-term spikes may reflect batch publication by courts rather than a change in real litigation activity. **Caution:** correlation with real-world litigation is not established.

2. **Observation:** Long-run moving averages (12M) move more smoothly than raw monthly counts. **Evidence:** `ma_12m` column. **Interpretation:** a longer-horizon trend exists independent of monthly noise. **Caution:** trend direction alone does not indicate cause.

3. **Observation:** Z-score/IQR methods flag a small number of extreme months. **Evidence:** `anomalies.csv`. **Interpretation:** these may correspond to database re-indexing events, not real spikes in disputes. **Caution:** always cross-check anomaly months against known law.go.kr publication-schedule changes before drawing conclusions.

## 13. AI Interpretation

If `OPENAI_API_KEY` is configured, `GET /api/v1/insights` returns an LLM-generated summary built ONLY from aggregated statistics (never raw case text), explicitly labeled and separated from the observed-fact sections above. See docs/AI_USAGE_LOG.md.

## 14. Limitations

**Precedent count increase does NOT equal actual litigation increase.** Confounders include: (a) search term composition and keyword overlap, (b) law.go.kr database coverage changes over time, (c) court publication practices (not all rulings are published), (d) shifting composition of courts contributing data, (e) changes to the search system itself (indexing, tokenization), and (f) the same underlying case may be counted more than once across repeated/overlapping keyword searches despite deduplication by ID.

## 15. Reproducibility

```bash
python backend/scripts/collect_precedents.py --start-date 2016-01-01 --end-date 2026-12-31
python backend/scripts/normalize_precedents.py
python backend/scripts/build_timeseries.py
python backend/scripts/run_analysis.py
python backend/scripts/run_decomposition.py
python backend/scripts/run_forecast.py
python backend/scripts/generate_report.py
```

## 16. AI Usage Log

See docs/AI_USAGE_LOG.md for the full log of how AI assistance was used to build this project.

## 17. Legal Disclaimer

This report and the accompanying dashboard/API are for statistical and educational purposes only. They are **NOT legal advice**, do not predict litigation outcomes, and must not be relied upon for any legal decision. Consult a licensed attorney for legal advice.
