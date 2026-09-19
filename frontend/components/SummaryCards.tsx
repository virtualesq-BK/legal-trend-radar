import { SummaryResponse, MonthlyPoint, AnomalyPoint } from "@/types";

export default function SummaryCards({
  summary,
  monthly,
  anomalies,
}: {
  summary: SummaryResponse;
  monthly: MonthlyPoint[];
  anomalies: AnomalyPoint[];
}) {
  const latestYoy = monthly.length ? monthly[monthly.length - 1].yoy_pct_change : null;
  const anomalyCount = anomalies.filter((a) => a.is_anomaly).length;

  const cards = [
    { label: "총 판례 검색결과 수", value: summary.total_records.toLocaleString() },
    {
      label: "최근 YoY 변화율",
      value: latestYoy != null ? `${latestYoy.toFixed(1)}%` : "N/A",
    },
    { label: "탐지된 이상치 수", value: anomalyCount.toString() },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
      {cards.map((c) => (
        <div key={c.label} className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 bg-white dark:bg-gray-900">
          <div className="text-sm text-gray-500 dark:text-gray-400">{c.label}</div>
          <div className="text-2xl font-semibold mt-1">{c.value}</div>
        </div>
      ))}
    </div>
  );
}
