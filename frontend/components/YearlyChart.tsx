"use client";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { YearlyPoint } from "@/types";

export default function YearlyChart({ data }: { data: YearlyPoint[] }) {
  return (
    <div className="w-full h-72">
      <h3 className="font-medium mb-2">연도별 건수</h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" />
          <YAxis />
          <Tooltip />
          <Bar dataKey="count" fill="#2563eb" name="건수" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
