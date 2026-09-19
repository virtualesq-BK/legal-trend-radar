"use client";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { DecompositionPoint } from "@/types";

export default function DecompositionChart({ data }: { data: DecompositionPoint[] }) {
  return (
    <div className="w-full grid grid-cols-1 gap-4">
      <h3 className="font-medium">STL 분해 (Trend / Seasonal / Residual)</h3>
      {(["observed", "trend", "seasonal", "resid"] as const).map((key) => (
        <div key={key} className="h-40">
          <div className="text-xs text-gray-500 mb-1">{key}</div>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" tick={{ fontSize: 9 }} interval={Math.ceil(data.length / 8)} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey={key} stroke="#2563eb" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ))}
    </div>
  );
}
