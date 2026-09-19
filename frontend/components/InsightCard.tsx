import { InsightsResponse } from "@/types";

export default function InsightCard({ insights }: { insights: InsightsResponse }) {
  if (!insights.available) {
    return (
      <div className="rounded-lg border border-yellow-300 bg-yellow-50 dark:bg-yellow-950 p-4 text-sm">
        {insights.reason || insights.summary || "AI 인사이트를 사용할 수 없습니다. OPENAI_API_KEY를 설정하세요."}
      </div>
    );
  }
  return (
    <div className="rounded-lg border border-gray-200 dark:border-gray-700 p-4 space-y-3">
      <div>
        <h3 className="font-medium">AI 요약 (해석 - 사실 아님)</h3>
        <p className="text-sm mt-1">{insights.summary}</p>
      </div>
      {insights.observations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold">관측된 사실 (Observations)</h4>
          <ul className="list-disc list-inside text-sm">
            {insights.observations.map((o, i) => (
              <li key={i}>{o}</li>
            ))}
          </ul>
        </div>
      )}
      {insights.interpretations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold">AI 해석 (Interpretations)</h4>
          <ul className="list-disc list-inside text-sm">
            {insights.interpretations.map((o, i) => (
              <li key={i}>{o}</li>
            ))}
          </ul>
        </div>
      )}
      {insights.limitations.length > 0 && (
        <div>
          <h4 className="text-sm font-semibold text-red-600">한계 (Limitations)</h4>
          <ul className="list-disc list-inside text-sm">
            {insights.limitations.map((o, i) => (
              <li key={i}>{o}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
