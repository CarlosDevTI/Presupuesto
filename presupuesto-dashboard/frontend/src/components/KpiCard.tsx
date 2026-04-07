import { ReactNode } from "react";

import { StatusTone } from "types/budget";
import { statusClasses, statusLabel } from "utils/format";

interface KpiCardProps {
  title: string;
  value: string;
  helper: string;
  status: StatusTone;
  icon: ReactNode;
}

export function KpiCard({ title, value, helper, status, icon }: KpiCardProps) {
  return (
    <article className="rounded-[24px] border border-slate-200 bg-white/95 p-5 shadow-panel">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">{title}</p>
          <p className="mt-4 text-3xl font-semibold text-ink">{value}</p>
        </div>
        <div className="rounded-full bg-mist p-3 text-tide">{icon}</div>
      </div>
      <div className="mt-5 flex items-center justify-between">
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClasses(status)}`}>
          {statusLabel(status)}
        </span>
        <span className="text-sm text-slate-500">{helper}</span>
      </div>
    </article>
  );
}
