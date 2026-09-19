"use client";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MonthlyPoint } from "@/types";

export default function TrendChart({ data }: { data: MonthlyPoint[] }) {
  return (
    <div className="w-full h-80">
      <h3 className="font-medium mb-2">월별 추이 (3M/12M 이동평균)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" tick={{ fontSize: 10 }} interval={Math.ceil(data.length / 12)} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="count" stroke="#2563eb" name="월별 건수" dot={false} />
          <Line type="monotone" dataKey="ma_3m" stroke="#f59e0b" name="3개월 이동평균" dot={false} />
          <Line type="monotone" dataKey="ma_12m" stroke="#10b981" name="12개월 이동평균" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
