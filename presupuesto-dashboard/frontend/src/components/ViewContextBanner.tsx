import { ViewContext } from "types/budget";

interface ViewContextBannerProps {
  context: ViewContext;
}

export function ViewContextBanner({ context }: ViewContextBannerProps) {
  return (
    <section className="rounded-[24px] border border-slate-200 bg-white/92 px-5 py-4 shadow-panel">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <p className="text-sm font-semibold text-ink">{context.label}</p>
          <p className="mt-2 text-sm text-slate-500">
            Base de calculo: {context.basis.accounts} {context.basis.double_count_prevention}
          </p>
        </div>
        <details className="group rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-600 lg:max-w-xl">
          <summary className="cursor-pointer list-none font-semibold text-tide">
            Como se calculan los indicadores
          </summary>
          <div className="mt-3 space-y-3">
            {context.kpi_formulas.map((formula) => (
              <div key={formula.key}>
                <p className="font-semibold text-ink">{formula.label}</p>
                <p>{formula.formula}</p>
              </div>
            ))}
          </div>
        </details>
      </div>
    </section>
  );
}
