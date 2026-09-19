#!/usr/bin/env python
"""Compute moving averages, YoY change, volatility, and anomalies (z-score + IQR)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib  # noqa: E402

matplotlib.use("Agg")  # headless - this script may run without a display
import matplotlib.pyplot as plt  # noqa: E402

# Keyword labels are Korean; DejaVu Sans (matplotlib's default) has no Hangul
# glyphs and silently renders them as missing-glyph boxes. Use a Korean-
# capable font when one is available (Malgun Gothic ships with Windows;
# AppleGothic on macOS; fall back to default elsewhere without erroring).
for _font in ("Malgun Gothic", "AppleGothic", "NanumGothic"):
    if _font in {f.name for f in matplotlib.font_manager.fontManager.ttflist}:
        plt.rcParams["font.family"] = _font
        break
plt.rcParams["axes.unicode_minus"] = False
import pandas as pd  # noqa: E402

from app.config import DATA_ANALYSIS_DIR, FIGURES_DIR  # noqa: E402
from app.services.anomaly_service import combined_anomalies  # noqa: E402
from app.services.trend_service import build_trend_table  # noqa: E402


def _plot_monthly_trend(trend: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(trend["period"], trend["count"], label="Monthly count", color="#1f77b4", linewidth=1.2)
    if "ma_3m" in trend:
        ax.plot(trend["period"], trend["ma_3m"], label="3-month MA", color="#ff7f0e")
    if "ma_12m" in trend:
        ax.plot(trend["period"], trend["ma_12m"], label="12-month MA", color="#2ca02c")
    ax.set_title("Monthly Precedent Search-Result Count with Moving Averages")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    ax.set_xticks(ax.get_xticks()[:: max(1, len(trend) // 12)])
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "monthly_trend.png", dpi=120)
    plt.close(fig)


def _plot_yearly_trend(yearly: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(yearly["year"].astype(str), yearly["count"], color="#1f77b4")
    ax.set_title("Yearly Precedent Search-Result Count")
    ax.set_xlabel("Year")
    ax.set_ylabel("Count")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "yearly_trend.png", dpi=120)
    plt.close(fig)


def _plot_keyword_trend(keyword_monthly: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    for keyword, group in keyword_monthly.groupby("search_keyword"):
        ax.plot(group["period"], group["count"], label=keyword)
    ax.set_title("Monthly Search-Result Count by Keyword")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    periods = sorted(keyword_monthly["period"].unique())
    ax.set_xticks(periods[:: max(1, len(periods) // 12)])
    ax.tick_params(axis="x", rotation=45)
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "keyword_trend.png", dpi=120)
    plt.close(fig)


def _plot_anomaly_trend(monthly: pd.DataFrame, anomalies: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(monthly["period"], monthly["count"], label="Monthly count", color="#1f77b4", linewidth=1.2)
    flagged = anomalies[anomalies["is_anomaly"]]
    for method, group in flagged.groupby("method"):
        ax.scatter(group["period"], group["count"], label=f"Anomaly ({method})", zorder=5)
    ax.set_title("Anomaly Timeline (Z-score and IQR methods)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Count")
    periods = sorted(monthly["period"].unique())
    ax.set_xticks(periods[:: max(1, len(periods) // 12)])
    ax.tick_params(axis="x", rotation=45)
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "anomaly_trend.png", dpi=120)
    plt.close(fig)


def main() -> int:
    monthly_path = DATA_ANALYSIS_DIR / "monthly.csv"
    if not monthly_path.exists():
        print("[BLOCKED] backend/data/analysis/monthly.csv not found. Run build_timeseries.py first.")
        return 2
    monthly = pd.read_csv(monthly_path)

    trend = build_trend_table(monthly)
    trend.to_csv(DATA_ANALYSIS_DIR / "monthly_trend.csv", index=False)

    anomalies = combined_anomalies(monthly)
    anomalies.to_csv(DATA_ANALYSIS_DIR / "anomalies.csv", index=False)

    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    _plot_monthly_trend(trend)

    yearly_path = DATA_ANALYSIS_DIR / "yearly.csv"
    if yearly_path.exists():
        _plot_yearly_trend(pd.read_csv(yearly_path))

    keyword_path = DATA_ANALYSIS_DIR / "keyword_monthly.csv"
    if keyword_path.exists():
        _plot_keyword_trend(pd.read_csv(keyword_path))

    _plot_anomaly_trend(monthly, anomalies)

    print(f"Wrote monthly_trend.csv ({len(trend)} rows), anomalies.csv ({len(anomalies)} rows), "
          f"and 4 figures to {FIGURES_DIR}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
