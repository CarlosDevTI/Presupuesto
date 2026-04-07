import { useEffect, useMemo } from "react";

import { BudgetBarChart } from "components/BudgetBarChart";
import { BudgetDonutChart } from "components/BudgetDonutChart";
import { FiltersBar } from "components/FiltersBar";
import { HierarchyTable } from "components/HierarchyTable";
import { InsightsPanel } from "components/InsightsPanel";
import { KpiCard } from "components/KpiCard";
import { RankingCard } from "components/RankingCard";
import { TrendChartCard } from "components/TrendChartCard";
import { ViewContextBanner } from "components/ViewContextBanner";
import { useDashboardStore } from "store/dashboardStore";
import { formatCompactMoney, formatPercent } from "utils/format";

const icons = {
  projected: "≈",
  executed: "◔",
  execution: "%",
  variance: "Δ",
  over: "!",
};

export function DashboardPage() {
  const {
    dashboard,
    filters,
    filtersMeta,
    initialize,
    loadDashboard,
    setFilters,
    clearFilters,
    loading,
    error,
  } = useDashboardStore();

  const queryKey = useMemo(() => JSON.stringify(filters), [filters]);

  useEffect(() => {
    void initialize();
  }, [initialize]);

  useEffect(() => {
    if (filtersMeta) {
      void loadDashboard();
    }
  }, [filtersMeta, loadDashboard, queryKey]);

  const kpis = dashboard?.summary.kpis;
  const context = dashboard?.summary.context;

  return (
    <div className="min-h-screen bg-slate-50 bg-halo px-4 py-6 sm:px-6 lg:px-10">
      <div className="mx-auto max-w-[1440px] space-y-6">
        <header className="rounded-[36px] border border-slate-200 bg-white/90 px-6 py-6 shadow-panel">
          <div className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
            <div className="flex items-center gap-6">
              <img src="/logo.png" alt="CONGENTE" className="h-20 w-auto object-contain" />
              <div>
                <h1 className="text-3xl font-semibold text-ink">Dashboard presupuestal corporativo</h1>
                <p className="mt-2 text-sm text-slate-500">
                  Lectura ejecutiva del presupuesto proyectado vs ejecutado para seguimiento gerencial.
                </p>
              </div>
            </div>
            <div className="rounded-full bg-mist px-4 py-2 text-sm font-semibold text-tide">
              CONGENTE · Control presupuestal 2026
            </div>
          </div>
        </header>

        <FiltersBar
          filters={filters}
          filtersMeta={filtersMeta}
          onFiltersChange={setFilters}
          onClearFilters={clearFilters}
        />

        {context ? <ViewContextBanner context={context} /> : null}

        {error ? (
          <section className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
            {error}
          </section>
        ) : null}

        {loading || !dashboard || !kpis ? (
          <section className="rounded-[28px] border border-slate-200 bg-white/90 px-6 py-12 text-center text-slate-500 shadow-panel">
            Cargando dashboard...
          </section>
        ) : (
          <>
            <div className="grid gap-4 lg:grid-cols-5">
              <KpiCard title="Presupuesto proyectado" value={formatCompactMoney(kpis.projected_total)} helper="Suma de cuentas hoja" status="green" icon={icons.projected} />
              <KpiCard title="Presupuesto ejecutado" value={formatCompactMoney(kpis.executed_total)} helper="Suma ejecutada visible" status={kpis.status} icon={icons.executed} />
              <KpiCard title="% ejecucion" value={formatPercent(kpis.execution_pct)} helper="Ejecutado / proyectado" status={kpis.status} icon={icons.execution} />
              <KpiCard title="Variacion" value={formatCompactMoney(kpis.variance_value)} helper="Ejecutado - proyectado" status={kpis.status} icon={icons.variance} />
              <KpiCard title="Cuentas sobre-ejecutadas" value={String(kpis.over_execution_count)} helper="Solo cuentas hoja" status={kpis.over_execution_count > 0 ? "red" : "green"} icon={icons.over} />
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
              <BudgetBarChart data={dashboard.trend.series} />
              <BudgetDonutChart data={dashboard.areas.areas} />
            </div>

            <div className="grid gap-6 xl:grid-cols-[1.35fr_0.65fr]">
              <TrendChartCard data={dashboard.trend.series} />
              <InsightsPanel insights={dashboard.insights.insights} />
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <RankingCard
                title="Areas con mayor gasto"
                subtitle="Ranking por ejecutado dentro de la vista actual"
                items={dashboard.rankings.top_areas}
                tone="tide"
              />
              <RankingCard
                title="Mayores sobre-ejecuciones"
                subtitle="Desviaciones positivas que requieren accion"
                items={dashboard.rankings.top_over_execution}
                tone="danger"
              />
            </div>

            <HierarchyTable nodes={dashboard.hierarchy.roots} />
          </>
        )}

        <footer className="pb-4 text-center text-sm text-slate-500">
          Desarrollado por el area de Gerencia TI
        </footer>
      </div>
    </div>
  );
}
