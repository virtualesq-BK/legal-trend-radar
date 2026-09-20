"use client";
import { useState } from "react";
import { api } from "@/lib/api";
import { ChatResponse, ChatToolCall } from "@/types";

const SUGGESTIONS = [
  "최근 이상치가 감지된 시점은 언제야?",
  "전체 기간 증감률을 알려줘",
  "Forecast 결과를 요약해줘",
];

// Demonstrates the Function Calling bonus feature end-to-end in the UI:
// the user's question goes to GPT with tool schemas only (no data), GPT
// decides which backend tool(s) to call, and the actual tool call trace is
// shown so it's visible *which* tool was invoked and with what arguments.
export default function ChatPanel() {
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function ask(q: string) {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = (await api.chat(q)) as ChatResponse;
      setResult(res);
    } catch (e) {
      setError(e instanceof Error ? e.message : "요청 중 오류가 발생했습니다.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h3 className="font-medium mb-2">AI에게 데이터 질문하기 (Function Calling)</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        GPT는 통계를 직접 알지 못하며, 질문에 답하기 위해 아래 도구(get_monthly_trend,
        get_anomalies, get_forecast 등) 중 필요한 것을 스스로 호출합니다. 실제로 호출된
        도구와 인자가 답변 아래에 표시됩니다.
      </p>
      <div className="flex flex-wrap gap-2 mb-3">
        {SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => {
              setQuestion(s);
              ask(s);
            }}
            className="text-xs rounded-full border border-gray-300 dark:border-gray-600 px-3 py-1
                       hover:bg-gray-50 dark:hover:bg-gray-700"
          >
            {s}
          </button>
        ))}
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (question.trim()) ask(question.trim());
        }}
        className="flex gap-2"
      >
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="질문을 입력하세요 (예: 이상치가 몇 개 감지됐어?)"
          className="flex-1 rounded-md border border-gray-300 dark:border-gray-600 px-3 py-1.5 text-sm
                     bg-white dark:bg-gray-800"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-md bg-blue-600 text-white px-4 py-1.5 text-sm disabled:opacity-50"
        >
          {loading ? "생각 중..." : "질문"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600 dark:text-red-400 mt-3">{error}</p>}

      {result && (
        <div className="mt-4 rounded-md border border-gray-200 dark:border-gray-700 p-3">
          <p className="text-sm whitespace-pre-wrap">{result.answer}</p>
          {result.tool_calls.length > 0 && (
            <div className="mt-3 border-t border-gray-200 dark:border-gray-700 pt-2">
              <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                호출된 도구 ({result.tool_calls.length}건):
              </div>
              <ul className="text-xs font-mono space-y-1">
                {result.tool_calls.map((tc: ChatToolCall, i: number) => (
                  <li key={i} className="text-gray-600 dark:text-gray-300">
                    {tc.name}({JSON.stringify(tc.arguments)})
                    {tc.error && <span className="text-red-600 dark:text-red-400"> → error: {tc.error}</span>}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
