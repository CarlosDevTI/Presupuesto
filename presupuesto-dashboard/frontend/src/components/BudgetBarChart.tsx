import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { TrendPoint } from "types/budget";
import { formatCompactMoney } from "utils/format";

import { SectionCard } from "./SectionCard";

interface BudgetBarChartProps {
  data: TrendPoint[];
}

export function BudgetBarChart({ data }: BudgetBarChartProps) {
  return (
    <SectionCard title="Proyectado vs ejecutado por mes" subtitle="Suma mensual sobre cuentas hoja normalizadas" className="h-full">
      <div className="h-[320px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} barGap={10}>
            <CartesianGrid strokeDasharray="3 3" stroke="#dbe4f0" />
            <XAxis dataKey="month_label" tickLine={false} axisLine={false} />
            <YAxis tickFormatter={formatCompactMoney} tickLine={false} axisLine={false} width={80} />
            <Tooltip formatter={(value: number) => formatCompactMoney(value)} />
            <Bar dataKey="projected" name="Proyectado" fill="#194d87" radius={[10, 10, 0, 0]} />
            <Bar dataKey="executed" name="Ejecutado" fill="#2a9d8f" radius={[10, 10, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </SectionCard>
  );
}
