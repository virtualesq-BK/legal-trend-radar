"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ConversationHistoryResponse, ConversationSession, ConversationTurn } from "@/types";

// Conversation history screen: lists saved chat sessions (from Firestore's
// `conversations` collection) and lets the user load one to re-view its
// question/answer messages.
export default function ConversationHistory() {
  const [sessions, setSessions] = useState<ConversationSession[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [turns, setTurns] = useState<ConversationTurn[]>([]);
  const [loadingTurns, setLoadingTurns] = useState(false);

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const rows = (await api.listSessions()) as ConversationSession[];
      setSessions(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : "대화 목록을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function loadSession(sessionId: string) {
    setSelected(sessionId);
    setLoadingTurns(true);
    try {
      const res = (await api.getConversation(sessionId)) as ConversationHistoryResponse;
      setTurns(res.turns);
    } catch (e) {
      setError(e instanceof Error ? e.message : "대화 내용을 불러오지 못했습니다.");
    } finally {
      setLoadingTurns(false);
    }
  }

  return (
    <div>
      <h3 className="font-medium mb-2">대화 기록</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        저장된 대화 세션 목록입니다. 클릭하면 해당 대화의 질문/답변을 다시 볼 수 있습니다.
      </p>
      {error && <p className="text-sm text-red-600 dark:text-red-400 mb-2">{error}</p>}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          {loading ? (
            <p className="text-sm text-gray-500">불러오는 중...</p>
          ) : sessions.length === 0 ? (
            <p className="text-sm text-gray-500">저장된 대화가 없습니다. AI 채팅에서 질문을 해보세요.</p>
          ) : (
            <ul className="space-y-1">
              {sessions.map((s) => (
                <li key={s.session_id}>
                  <button
                    onClick={() => loadSession(s.session_id)}
                    className={`w-full text-left rounded-md border px-3 py-2 text-sm transition-colors ${
                      selected === s.session_id
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-950"
                        : "border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800"
                    }`}
                  >
                    <div className="font-medium truncate">{s.session_id}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400 truncate">
                      {s.last_message} · {s.turn_count}건
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-md border border-gray-200 dark:border-gray-700 p-3 min-h-[8rem]">
          {!selected ? (
            <p className="text-sm text-gray-500">왼쪽에서 대화를 선택하세요.</p>
          ) : loadingTurns ? (
            <p className="text-sm text-gray-500">불러오는 중...</p>
          ) : (
            <div className="space-y-3">
              {turns.map((t, i) => (
                <div key={i} className="text-sm">
                  <div className="font-medium text-blue-700 dark:text-blue-300">Q. {t.user_message}</div>
                  <div className="mt-1 whitespace-pre-wrap">A. {t.answer}</div>
                  {t.tool_calls.length > 0 && (
                    <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      호출된 도구: {t.tool_calls.map((tc) => tc.name).join(", ")}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
