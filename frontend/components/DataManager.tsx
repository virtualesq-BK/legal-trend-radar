"use client";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { DataRecord } from "@/types";

// Data Management (CRUD) screen: add / edit / delete (date, value, memo)
// records stored in Firestore's `data` collection. The list refreshes after
// every mutation and a save-result message confirms success/failure.
export default function DataManager() {
  const [records, setRecords] = useState<DataRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);

  const [date, setDate] = useState("");
  const [value, setValue] = useState("");
  const [memo, setMemo] = useState("");

  const [editingId, setEditingId] = useState<string | null>(null);
  const [editDraft, setEditDraft] = useState<{ date: string; value: string; memo: string }>({
    date: "",
    value: "",
    memo: "",
  });

  async function refresh() {
    setLoading(true);
    setError(null);
    try {
      const rows = (await api.listRecords()) as DataRecord[];
      setRecords(rows);
    } catch (e) {
      setError(e instanceof Error ? e.message : "목록을 불러오지 못했습니다.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    refresh();
  }, []);

  async function handleCreate(e: React.FormEvent) {
    e.preventDefault();
    setStatus(null);
    try {
      await api.createRecord(date, parseFloat(value), memo || null);
      setStatus("저장되었습니다.");
      setDate("");
      setValue("");
      setMemo("");
      refresh();
    } catch (e) {
      setStatus(`저장 실패: ${e instanceof Error ? e.message : e}`);
    }
  }

  function startEdit(r: DataRecord) {
    setEditingId(r.id);
    setEditDraft({ date: r.date, value: String(r.value), memo: r.memo ?? "" });
  }

  async function handleUpdate(id: string) {
    setStatus(null);
    try {
      await api.updateRecord(id, {
        date: editDraft.date,
        value: parseFloat(editDraft.value),
        memo: editDraft.memo,
      });
      setStatus("수정되었습니다.");
      setEditingId(null);
      refresh();
    } catch (e) {
      setStatus(`수정 실패: ${e instanceof Error ? e.message : e}`);
    }
  }

  async function handleDelete(id: string) {
    setStatus(null);
    try {
      await api.deleteRecord(id);
      setStatus("삭제되었습니다.");
      refresh();
    } catch (e) {
      setStatus(`삭제 실패: ${e instanceof Error ? e.message : e}`);
    }
  }

  return (
    <div>
      <h3 className="font-medium mb-2">데이터 관리 (CRUD)</h3>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">
        직접 (date, value, memo) 데이터를 추가/수정/삭제할 수 있습니다. AI 채팅에서
        &quot;내가 저장한 데이터&quot;를 물어보면 여기 저장된 값을 근거로 답변합니다.
      </p>

      <form onSubmit={handleCreate} className="flex flex-wrap gap-2 mb-3">
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
          className="rounded-md border border-gray-300 dark:border-gray-600 px-2 py-1.5 text-sm bg-white dark:bg-gray-800"
        />
        <input
          type="number"
          step="any"
          placeholder="값 (value)"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          required
          className="w-28 rounded-md border border-gray-300 dark:border-gray-600 px-2 py-1.5 text-sm bg-white dark:bg-gray-800"
        />
        <input
          type="text"
          placeholder="메모 (선택)"
          value={memo}
          onChange={(e) => setMemo(e.target.value)}
          className="flex-1 min-w-[10rem] rounded-md border border-gray-300 dark:border-gray-600 px-2 py-1.5 text-sm bg-white dark:bg-gray-800"
        />
        <button type="submit" className="rounded-md bg-blue-600 text-white px-4 py-1.5 text-sm">
          추가
        </button>
      </form>

      {status && <p className="text-sm mb-2 text-green-700 dark:text-green-400">{status}</p>}
      {error && <p className="text-sm mb-2 text-red-600 dark:text-red-400">{error}</p>}

      {loading ? (
        <p className="text-sm text-gray-500">불러오는 중...</p>
      ) : records.length === 0 ? (
        <p className="text-sm text-gray-500">저장된 데이터가 없습니다.</p>
      ) : (
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
              <th className="py-1.5 pr-2">날짜</th>
              <th className="py-1.5 pr-2">값</th>
              <th className="py-1.5 pr-2">메모</th>
              <th className="py-1.5 pr-2 text-right">작업</th>
            </tr>
          </thead>
          <tbody>
            {records.map((r) => (
              <tr key={r.id} className="border-b border-gray-100 dark:border-gray-800">
                {editingId === r.id ? (
                  <>
                    <td className="py-1.5 pr-2">
                      <input
                        type="date"
                        value={editDraft.date}
                        onChange={(e) => setEditDraft({ ...editDraft, date: e.target.value })}
                        className="rounded border border-gray-300 dark:border-gray-600 px-1 py-0.5 bg-white dark:bg-gray-800"
                      />
                    </td>
                    <td className="py-1.5 pr-2">
                      <input
                        type="number"
                        step="any"
                        value={editDraft.value}
                        onChange={(e) => setEditDraft({ ...editDraft, value: e.target.value })}
                        className="w-20 rounded border border-gray-300 dark:border-gray-600 px-1 py-0.5 bg-white dark:bg-gray-800"
                      />
                    </td>
                    <td className="py-1.5 pr-2">
                      <input
                        type="text"
                        value={editDraft.memo}
                        onChange={(e) => setEditDraft({ ...editDraft, memo: e.target.value })}
                        className="w-full rounded border border-gray-300 dark:border-gray-600 px-1 py-0.5 bg-white dark:bg-gray-800"
                      />
                    </td>
                    <td className="py-1.5 pr-2 text-right whitespace-nowrap">
                      <button onClick={() => handleUpdate(r.id)} className="text-blue-600 dark:text-blue-400 mr-2">
                        저장
                      </button>
                      <button onClick={() => setEditingId(null)} className="text-gray-500">
                        취소
                      </button>
                    </td>
                  </>
                ) : (
                  <>
                    <td className="py-1.5 pr-2">{r.date}</td>
                    <td className="py-1.5 pr-2">{r.value}</td>
                    <td className="py-1.5 pr-2 text-gray-600 dark:text-gray-300">{r.memo || "-"}</td>
                    <td className="py-1.5 pr-2 text-right whitespace-nowrap">
                      <button onClick={() => startEdit(r)} className="text-blue-600 dark:text-blue-400 mr-2">
                        수정
                      </button>
                      <button onClick={() => handleDelete(r.id)} className="text-red-600 dark:text-red-400">
                        삭제
                      </button>
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
