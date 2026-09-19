"use client";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { KeywordPoint } from "@/types";

const COLORS = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#14b8a6"];

export default function KeywordChart({ data }: { data: KeywordPoint[] }) {
  const keywords = Array.from(new Set(data.map((d) => d.search_keyword)));
  const periods = Array.from(new Set(data.map((d) => d.period))).sort();
  const pivoted = periods.map((period) => {
    const row: Record<string, string | number> = { period };
    for (const kw of keywords) {
      const match = data.find((d) => d.period === period && d.search_keyword === kw);
      row[kw] = match ? match.count : 0;
    }
    return row;
  });

  return (
    <div className="w-full h-80">
      <h3 className="font-medium mb-2">키워드별 추이</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={pivoted}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" tick={{ fontSize: 10 }} interval={Math.ceil(pivoted.length / 12)} />
          <YAxis />
          <Tooltip />
          <Legend />
          {keywords.map((kw, i) => (
            <Line key={kw} type="monotone" dataKey={kw} stroke={COLORS[i % COLORS.length]} dot={false} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
