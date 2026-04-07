import { DashboardFilters, FiltersResponse } from "types/budget";

interface FiltersBarProps {
  filters: DashboardFilters;
  filtersMeta?: FiltersResponse;
  onFiltersChange: (partial: Partial<DashboardFilters>) => void;
  onClearFilters: () => void;
}

export function FiltersBar({ filters, filtersMeta, onFiltersChange, onClearFilters }: FiltersBarProps) {
  const months = filtersMeta?.months ?? [];

  const toggleMonth = (monthKey: string) => {
    const isActive = filters.months.includes(monthKey);
    const nextMonths = isActive
      ? filters.months.filter((value) => value !== monthKey)
      : [...filters.months, monthKey];
    onFiltersChange({ months: nextMonths });
  };

  return (
    <section className="rounded-[28px] border border-slate-200 bg-white/90 p-5 shadow-panel">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-end xl:justify-between">
        <div className="space-y-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Meses visibles</p>
            <div className="mt-3 flex flex-wrap gap-2">
              {months.map((month) => {
                const active = filters.months.includes(month.month_key);
                return (
                  <button
                    key={month.month_key}
                    type="button"
                    onClick={() => toggleMonth(month.month_key)}
                    className={`rounded-full px-4 py-2 text-sm font-semibold transition ${
                      active ? "bg-tide text-white" : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                    }`}
                  >
                    {month.month_label}
                  </button>
                );
              })}
            </div>
            <p className="mt-3 text-sm text-slate-500">
              Sin seleccion de mes, la vista usa todos los meses disponibles del dataset.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            <label className="text-sm text-slate-500">
              Area
              <select
                value={filters.area ?? ""}
                onChange={(event) => onFiltersChange({ area: event.target.value || undefined })}
                className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700"
              >
                <option value="">Todas las areas</option>
                {filtersMeta?.areas.map((area) => (
                  <option key={area} value={area}>
                    {area}
                  </option>
                ))}
              </select>
            </label>
            {filtersMeta?.has_responsible ? (
              <label className="text-sm text-slate-500">
                Responsable
                <select
                  value={filters.responsible ?? ""}
                  onChange={(event) => onFiltersChange({ responsible: event.target.value || undefined })}
                  className="mt-2 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-slate-700"
                >
                  <option value="">Todos los responsables</option>
                  {filtersMeta?.responsibles.map((responsible) => (
                    <option key={responsible} value={responsible}>
                      {responsible}
                    </option>
                  ))}
                </select>
              </label>
            ) : null}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={onClearFilters}
            className="rounded-full border border-slate-300 px-5 py-3 text-sm font-semibold text-slate-600 transition hover:border-slate-400 hover:text-slate-800"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </section>
  );
}
