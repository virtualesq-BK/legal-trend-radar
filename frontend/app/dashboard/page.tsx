"use client";
import { useEffect, useState } from "react";
import { api, ApiBlockedError } from "@/lib/api";
import {
  SummaryResponse,
  MonthlyPoint,
  YearlyPoint,
  KeywordPoint,
  AnomalyPoint,
  DecompositionPoint,
  ForecastResponse,
  InsightsResponse,
  StatisticsResponse,
} from "@/types";
import SummaryCards from "@/components/SummaryCards";
import TrendChart from "@/components/TrendChart";
import MovingAverageChart from "@/components/MovingAverageChart";
import YearlyChart from "@/components/YearlyChart";
import KeywordChart from "@/components/KeywordChart";
import AnomalyChart from "@/components/AnomalyChart";
import DecompositionChart from "@/components/DecompositionChart";
import ForecastChart from "@/components/ForecastChart";
import InsightCard from "@/components/InsightCard";
import YoYChart from "@/components/YoYChart";
import StatisticsPanel from "@/components/StatisticsPanel";
import ExportButtons from "@/components/ExportButtons";
import ThemeToggle from "@/components/ThemeToggle";
import ChatPanel from "@/components/ChatPanel";

interface DashboardData {
  summary: SummaryResponse;
  monthly: MonthlyPoint[];
  yearly: YearlyPoint[];
  keywords: KeywordPoint[];
  anomalies: AnomalyPoint[];
  decomposition: DecompositionPoint[] | null;
  forecast: ForecastResponse | null;
  insights: InsightsResponse;
  statistics: StatisticsResponse | null;
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [summary, monthly, yearly, keywords, anomalies, insights] = await Promise.all([
          api.summary() as Promise<SummaryResponse>,
          api.monthly() as Promise<MonthlyPoint[]>,
          api.yearly() as Promise<YearlyPoint[]>,
          api.keywords() as Promise<KeywordPoint[]>,
          api.anomalies() as Promise<AnomalyPoint[]>,
          api.insights() as Promise<InsightsResponse>,
        ]);
        // Decomposition/forecast may legitimately be unavailable (too few months) -
        // treat that as "not yet available" rather than a page-level error.
        let decomposition: DecompositionPoint[] | null = null;
        let forecast: ForecastResponse | null = null;
        try {
          decomposition = (await api.decomposition()) as DecompositionPoint[];
        } catch {
          decomposition = null;
        }
        try {
          forecast = (await api.forecast()) as ForecastResponse;
        } catch {
          forecast = null;
        }
        let statistics: StatisticsResponse | null = null;
        try {
          statistics = (await api.statistics()) as StatisticsResponse;
        } catch {
          statistics = null;
        }
        if (!cancelled) {
          setData({
            summary,
            monthly,
            yearly,
            keywords,
            anomalies,
            decomposition,
            forecast,
            insights,
            statistics,
          });
        }
      } catch (e) {
        if (!cancelled) {
          const msg =
            e instanceof ApiBlockedError
              ? e.detail
              : "알 수 없는 오류가 발생했습니다.";
          setError(msg);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) {
    return <div className="p-8 text-center text-gray-500">데이터를 불러오는 중입니다...</div>;
  }

  if (error) {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <div className="rounded-lg border border-red-300 bg-red-50 dark:bg-red-950 p-6">
          <h2 className="font-semibold text-red-700 dark:text-red-300 mb-2">데이터를 불러올 수 없습니다</h2>
          <p className="text-sm whitespace-pre-wrap">{error}</p>
          <p className="text-xs text-gray-500 mt-3">
            해결 방법: LAW_API_OC를 .env에 설정한 뒤 데이터 수집 파이프라인
            (collect_precedents.py → normalize_precedents.py → build_timeseries.py →
            run_analysis.py)을 실행하세요.
          </p>
        </div>
      </div>
    );
  }

  if (!data) return null;

  if (!data.summary.sufficient) {
    return (
      <div className="p-8 max-w-2xl mx-auto">
        <div className="rounded-lg border border-yellow-300 bg-yellow-50 dark:bg-yellow-950 p-6">
          <h2 className="font-semibold mb-2">분석에 필요한 데이터가 부족합니다</h2>
          <p className="text-sm">
            현재 수집 건수: {data.summary.total_records} / 최소 요구 건수: {data.summary.min_required}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto flex flex-col gap-8">
      <header className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">Legal Trend Radar 대시보드</h1>
          <p className="text-sm text-gray-500">
            데이터 출처: 국가법령정보센터 Open API · 수집 시각: {data.summary.data_collected_at ?? "N/A"}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <ExportButtons />
          <ThemeToggle />
        </div>
      </header>

      <SummaryCards summary={data.summary} monthly={data.monthly} anomalies={data.anomalies} />

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <StatisticsPanel stats={data.statistics} />
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <TrendChart data={data.monthly} />
      </section>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <YearlyChart data={data.yearly} />
        </section>
        <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
          <MovingAverageChart data={data.monthly} />
        </section>
      </div>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <YoYChart data={data.monthly} />
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <KeywordChart data={data.keywords} />
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <AnomalyChart data={data.anomalies} />
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        {data.decomposition ? (
          <DecompositionChart data={data.decomposition} />
        ) : (
          <p className="text-sm text-gray-500">
            STL 분해를 수행하려면 최소 24개월의 데이터가 필요합니다. 현재는 사용할 수 없습니다.
          </p>
        )}
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        {data.forecast ? (
          <ForecastChart data={data.forecast} />
        ) : (
          <p className="text-sm text-gray-500">예측을 수행하기에 데이터가 충분하지 않습니다.</p>
        )}
      </section>

      <section>
        <InsightCard insights={data.insights} />
      </section>

      <section className="rounded-lg border border-gray-200 dark:border-gray-700 p-4">
        <ChatPanel />
      </section>

      <footer className="text-xs text-gray-500 border-t pt-4 mt-4">
        <p>
          본 서비스는 국가법령정보센터 Open API의 공개 판례 검색결과를 통계적으로 분석한 것으로,
          <strong> 법률 자문이 아니며 소송 결과를 예측하지 않습니다.</strong> 법률적 판단이 필요한 경우
          반드시 변호사 등 전문가와 상담하시기 바랍니다.
        </p>
      </footer>
    </div>
  );
}
