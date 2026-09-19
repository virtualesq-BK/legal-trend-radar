"use client";
import { CartesianGrid, ResponsiveContainer, Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis } from "recharts";
import { AnomalyPoint } from "@/types";

export default function AnomalyChart({ data }: { data: AnomalyPoint[] }) {
  const zscore = data.filter((d) => d.method === "zscore");
  const anomalies = zscore.filter((d) => d.is_anomaly);

  return (
    <div className="w-full h-72">
      <h3 className="font-medium mb-2">이상치 타임라인 (Z-score)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" type="category" allowDuplicatedCategory={false} tick={{ fontSize: 10 }} />
          <YAxis dataKey="count" />
          <ZAxis range={[60, 60]} />
          <Tooltip />
          <Scatter data={zscore} fill="#93c5fd" name="정상" />
          <Scatter data={anomalies} fill="#ef4444" name="이상치" />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}
