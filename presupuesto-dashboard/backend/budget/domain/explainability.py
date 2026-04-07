from __future__ import annotations

from budget.domain.filters import FilterParams

KPI_FORMULAS = [
    {
        "key": "projected_total",
        "label": "Presupuesto proyectado",
        "formula": "Suma del proyectado de las cuentas hoja incluidas en la vista.",
    },
    {
        "key": "executed_total",
        "label": "Presupuesto ejecutado",
        "formula": "Suma del ejecutado de las cuentas hoja incluidas en la vista.",
    },
    {
        "key": "execution_pct",
        "label": "% ejecucion",
        "formula": "ejecutado_total / projected_total * 100, con proteccion si projected_total = 0.",
    },
    {
        "key": "variance_value",
        "label": "Variacion",
        "formula": "executed_total - projected_total.",
    },
    {
        "key": "over_execution_count",
        "label": "Cuentas sobre-ejecutadas",
        "formula": "Cantidad de cuentas hoja cuya suma ejecutada supera su suma proyectada en la vista actual.",
    },
]

INSIGHT_CRITERIA = [
    {"type": "area_over_execution", "criterion": "Area con mayor sobre-ejecucion positiva por valor."},
    {"type": "month_over_month", "criterion": "Cambio del ejecutado del ultimo mes visible frente al mes visible anterior."},
    {"type": "budget_concentration", "criterion": "Participacion del top 3 de areas sobre el presupuesto proyectado visible."},
    {"type": "critical_account", "criterion": "Cuenta hoja con mayor sobre-ejecucion positiva por valor."},
]


def build_view_context(filters: FilterParams, available_months: list[dict]) -> dict:
    month_lookup = {item["month_key"]: item["month_label"] for item in available_months}
    selected_months = [month_lookup.get(month, month) for month in filters.months]
    consolidated = not filters.months and not filters.area and not filters.responsible

    month_scope = "todos los meses disponibles" if consolidated else _format_list(selected_months) or "meses filtrados"
    area_scope = "todas las areas normalizadas" if not filters.area else filters.area
    responsible_scope = "todos los responsables disponibles" if not filters.responsible else filters.responsible

    label = (
        "Vista consolidada: todos los meses disponibles y todas las areas normalizadas."
        if consolidated
        else f"Vista filtrada: {month_scope}, {area_scope}."
    )

    return {
        "mode": "consolidated" if consolidated else "filtered",
        "label": label,
        "basis": {
            "months": month_scope,
            "areas": area_scope,
            "responsibles": responsible_scope,
            "accounts": "Solo cuentas hoja normalizadas.",
            "double_count_prevention": (
                "KPIs, graficas e insights usan solo nodos hoja. La tabla jerarquica reconstruye padres por prefijo para evitar doble conteo."
            ),
        },
        "kpi_formulas": KPI_FORMULAS,
        "insight_criteria": INSIGHT_CRITERIA,
    }


def _format_list(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} y {values[1]}"
    return f"{', '.join(values[:-1])} y {values[-1]}"
