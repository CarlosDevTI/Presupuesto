import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

import { AreaPoint } from "types/budget";
import { formatCompactMoney, formatPercent } from "utils/format";

import { SectionCard } from "./SectionCard";

const COLORS = ["#194d87", "#2a9d8f", "#d1a31c", "#6c8ebf", "#203047", "#7c3aed"];

interface BudgetDonutChartProps {
  data: AreaPoint[];
}

export function BudgetDonutChart({ data }: BudgetDonutChartProps) {
  return (
    <SectionCard title="Distribucion del presupuesto por areas" subtitle="Donut y listado lateral usan exactamente la misma agregacion normalizada" className="h-full">
      <div className="grid gap-4 lg:grid-cols-[1.1fr_0.9fr] lg:items-center">
        <div className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={data} dataKey="projected" nameKey="name" innerRadius={72} outerRadius={110} paddingAngle={3}>
                {data.map((entry, index) => (
                  <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value: number) => formatCompactMoney(value)} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="space-y-3">
          {data.slice(0, 5).map((entry, index) => (
            <article key={entry.name} className="flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="h-3 w-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                <div>
                  <p className="text-sm font-semibold text-ink">{entry.name || "Sin area"}</p>
                  <p className="text-xs text-slate-500">{formatCompactMoney(entry.projected)}</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-slate-600">{formatPercent(entry.share_pct)}</span>
            </article>
          ))}
        </div>
      </div>
    </SectionCard>
  );
}
