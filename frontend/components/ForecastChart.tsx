"use client";
import { Area, CartesianGrid, ComposedChart, Legend, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ForecastResponse } from "@/types";

export default function ForecastChart({ data }: { data: ForecastResponse }) {
  return (
    <div className="w-full">
      <h3 className="font-medium mb-2">예측 (Forecast)</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data.points}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fontSize: 10 }} interval={Math.ceil(data.points.length / 12)} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Area dataKey="upper_ci" stroke="none" fill="#93c5fd" fillOpacity={0.3} name="신뢰구간 상한" />
            <Area dataKey="lower_ci" stroke="none" fill="#ffffff" fillOpacity={1} name="신뢰구간 하한" />
            <Line type="monotone" dataKey="actual" stroke="#2563eb" name="실측값" dot={false} />
            <Line type="monotone" dataKey="forecast" stroke="#f59e0b" strokeDasharray="5 5" name="예측값" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="text-xs text-gray-500 mt-2">{data.disclaimer}</p>
    </div>
  );
}
