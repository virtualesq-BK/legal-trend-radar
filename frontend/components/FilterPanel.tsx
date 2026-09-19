"use client";
import { useState } from "react";

export interface Filters {
  startDate: string;
  endDate: string;
  keyword: string;
  courtType: string;
}

export default function FilterPanel({
  keywords,
  courts,
  onChange,
}: {
  keywords: string[];
  courts: string[];
  onChange: (f: Filters) => void;
}) {
  const [filters, setFilters] = useState<Filters>({
    startDate: "",
    endDate: "",
    keyword: "",
    courtType: "",
  });

  function update(partial: Partial<Filters>) {
    const next = { ...filters, ...partial };
    setFilters(next);
    onChange(next);
  }

  return (
    <div className="flex flex-wrap gap-3 items-end rounded-lg border border-gray-200 dark:border-gray-700 p-4">
      <div>
        <label className="block text-xs text-gray-500">시작일</label>
        <input
          type="date"
          className="border rounded px-2 py-1 text-sm bg-transparent"
          value={filters.startDate}
          onChange={(e) => update({ startDate: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-xs text-gray-500">종료일</label>
        <input
          type="date"
          className="border rounded px-2 py-1 text-sm bg-transparent"
          value={filters.endDate}
          onChange={(e) => update({ endDate: e.target.value })}
        />
      </div>
      <div>
        <label className="block text-xs text-gray-500">키워드</label>
        <select
          className="border rounded px-2 py-1 text-sm bg-transparent"
          value={filters.keyword}
          onChange={(e) => update({ keyword: e.target.value })}
        >
          <option value="">전체</option>
          {keywords.map((k) => (
            <option key={k} value={k}>
              {k}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label className="block text-xs text-gray-500">법원 유형</label>
        <select
          className="border rounded px-2 py-1 text-sm bg-transparent"
          value={filters.courtType}
          onChange={(e) => update({ courtType: e.target.value })}
        >
          <option value="">전체</option>
          {courts.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}
