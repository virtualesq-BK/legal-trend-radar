"use client";
import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MonthlyPoint } from "@/types";

// New visualization (bonus): plots the yoy_pct_change field that already
// exists on each monthly point but wasn't shown as its own chart anywhere -
// makes "이 달이 작년 동월 대비 늘었는지/줄었는지" visible at a glance.
export default function YoYChart({ data }: { data: MonthlyPoint[] }) {
  const rows = data.filter((d) => d.yoy_pct_change !== null && d.yoy_pct_change !== undefined);

  return (
    <div className="w-full h-80">
      <h3 className="font-medium mb-2">전년 동월 대비 증감률 (YoY %)</h3>
      {rows.length === 0 ? (
        <p className="text-sm text-gray-500">YoY를 계산하려면 최소 13개월의 데이터가 필요합니다.</p>
      ) : (
        <ResponsiveContainer width="100%" height="90%">
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="period" tick={{ fontSize: 10 }} interval={Math.ceil(rows.length / 12)} />
            <YAxis unit="%" />
            <Tooltip formatter={(v) => `${Number(v).toFixed(1)}%`} />
            <Bar dataKey="yoy_pct_change" name="YoY %">
              {rows.map((row, i) => (
                <Cell key={i} fill={(row.yoy_pct_change ?? 0) >= 0 ? "#16a34a" : "#dc2626"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
