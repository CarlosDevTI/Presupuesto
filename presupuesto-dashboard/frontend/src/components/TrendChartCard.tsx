import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { TrendPoint } from "types/budget";
import { formatCompactMoney } from "utils/format";

import { SectionCard } from "./SectionCard";

interface TrendChartCardProps {
  data: TrendPoint[];
}

export function TrendChartCard({ data }: TrendChartCardProps) {
  return (
    <SectionCard title="Tendencia mensual de ejecucion" subtitle="Lectura cronologica de proyectado y ejecutado" className="h-full">
      <div className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
            <XAxis dataKey="month_label" tickLine={false} axisLine={false} />
            <YAxis tickFormatter={formatCompactMoney} tickLine={false} axisLine={false} width={80} />
            <Tooltip formatter={(value: number) => formatCompactMoney(value)} />
            <Legend />
            <Line type="monotone" dataKey="projected" name="Proyectado" stroke="#194d87" strokeWidth={3} dot={{ r: 4 }} />
            <Line type="monotone" dataKey="executed" name="Ejecutado" stroke="#2a9d8f" strokeWidth={3} dot={{ r: 4 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}
