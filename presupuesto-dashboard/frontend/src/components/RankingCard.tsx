import { RankingItem } from "types/budget";
import { formatCompactMoney, formatPercent } from "utils/format";

import { SectionCard } from "./SectionCard";

interface RankingCardProps {
  title: string;
  subtitle: string;
  items: RankingItem[];
  tone: "tide" | "danger";
}

export function RankingCard({ title, subtitle, items, tone }: RankingCardProps) {
  const accent = tone === "danger" ? "bg-rose-500" : "bg-tide";

  return (
    <SectionCard title={title} subtitle={subtitle} className="h-full">
      <div className="space-y-3">
        {items.length ? (
          items.map((item) => (
            <article key={`${item.account_code ?? item.name}-${item.executed}`} className="rounded-2xl bg-slate-50 p-4">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-sm font-semibold text-ink">{item.account_name ?? item.name ?? item.area}</p>
                  <p className="mt-1 text-xs text-slate-500">
                    Ejecutado {formatCompactMoney(item.executed)}
                    {typeof item.execution_pct === "number" ? ` · ${formatPercent(item.execution_pct)}` : ""}
                  </p>
                </div>
                <div className="flex items-center gap-2 text-sm font-semibold text-slate-600">
                  <span className={`h-2.5 w-2.5 rounded-full ${accent}`} />
                  {formatCompactMoney(item.variance_value)}
                </div>
              </div>
            </article>
          ))
        ) : (
          <p className="text-sm text-slate-500">No hay datos disponibles para este ranking.</p>
        )}
      </div>
    </SectionCard>
  );
}
