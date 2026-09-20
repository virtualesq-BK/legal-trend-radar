import { StatisticsResponse } from "@/types";

// Displays the enriched metrics from GET /api/v1/data/statistics that go
// beyond the basic summary card row (median/std, full-period growth rate,
// anomaly rate, peak/trough month).
export default function StatisticsPanel({ stats }: { stats: StatisticsResponse | null }) {
  if (!stats) return null;

  const pct = (v: number | null) => (v == null ? "N/A" : `${v.toFixed(1)}%`);
  const num = (v: number | null) => (v == null ? "N/A" : v.toLocaleString(undefined, { maximumFractionDigits: 1 }));

  const items: { label: string; value: string }[] = [
    { label: "중앙값 (월별)", value: num(stats.median_monthly_count) },
    { label: "표준편차 (월별)", value: num(stats.std_monthly_count) },
    { label: "전체 기간 증감률", value: pct(stats.growth_rate_pct_full_period) },
    { label: "이상치 비율", value: pct(stats.anomaly_rate_pct) },
    {
      label: "최고점",
      value: stats.peak_month ? `${stats.peak_month.period} (${stats.peak_month.count}건)` : "N/A",
    },
    {
      label: "최저점",
      value: stats.trough_month ? `${stats.trough_month.period} (${stats.trough_month.count}건)` : "N/A",
    },
  ];

  return (
    <div>
      <h3 className="font-medium mb-2">상세 통계 (Statistics API)</h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
        {items.map((item) => (
          <div key={item.label} className="rounded-md border border-gray-200 dark:border-gray-700 p-3">
            <div className="text-xs text-gray-500 dark:text-gray-400">{item.label}</div>
            <div className="text-lg font-semibold mt-0.5">{item.value}</div>
          </div>
        ))}
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">{stats.note}</p>
    </div>
  );
}
