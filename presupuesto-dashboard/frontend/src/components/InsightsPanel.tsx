import { InsightItem } from "types/budget";

import { SectionCard } from "./SectionCard";

const severityClasses: Record<string, string> = {
  danger: "border-rose-200 bg-rose-50 text-rose-700",
  warning: "border-amber-200 bg-amber-50 text-amber-700",
  positive: "border-emerald-200 bg-emerald-50 text-emerald-700",
  info: "border-sky-200 bg-sky-50 text-sky-700",
  neutral: "border-slate-200 bg-slate-50 text-slate-600",
};

interface InsightsPanelProps {
  insights: InsightItem[];
}

export function InsightsPanel({ insights }: InsightsPanelProps) {
  return (
    <SectionCard title="Insights automaticos" subtitle="Hallazgos calculados desde la misma base consolidada del dashboard" className="h-full">
      <div className="space-y-3">
        {insights.map((insight, index) => (
          <article
            key={`${insight.type}-${index}`}
            className={`rounded-2xl border px-4 py-3 text-sm leading-6 ${severityClasses[insight.severity] ?? severityClasses.neutral}`}
          >
            <p>{insight.message}</p>
            <p className="mt-2 text-xs opacity-80">Criterio: {insight.criterion}</p>
          </article>
        ))}
      </div>
    </SectionCard>
  );
}
