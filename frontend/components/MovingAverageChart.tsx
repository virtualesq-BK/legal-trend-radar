"use client";
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { MonthlyPoint } from "@/types";

export default function MovingAverageChart({ data }: { data: MonthlyPoint[] }) {
  return (
    <div className="w-full h-72">
      <h3 className="font-medium mb-2">변동성 (Rolling Volatility)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" tick={{ fontSize: 10 }} interval={Math.ceil(data.length / 12)} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="volatility" stroke="#ef4444" name="변동성(표준편차)" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
