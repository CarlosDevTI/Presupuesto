from __future__ import annotations

import pandas as pd

from .aggregations import aggregate_by_account, aggregate_by_area, aggregate_monthly
from .kpis import build_summary_metrics


def build_insights(leaf_df: pd.DataFrame) -> list[dict]:
    """Genera insights ejecutivos solo desde cuentas hoja para mantener una base unica y auditable."""
    if leaf_df.empty:
        return [
            {
                "type": "info",
                "severity": "neutral",
                "message": "No hay datos disponibles para generar insights con los filtros actuales.",
                "criterion": "No existen cuentas hoja en la seleccion actual.",
            }
        ]

    insights: list[dict] = []
    summary = build_summary_metrics(leaf_df)
    area_group = aggregate_by_area(leaf_df)
    month_group = aggregate_monthly(leaf_df)
    account_group = aggregate_by_account(leaf_df)

    top_over_area = area_group[area_group["variance_value"] > 0].head(1)
    if not top_over_area.empty:
        area_row = top_over_area.iloc[0]
        insights.append(
            {
                "type": "area_over_execution",
                "severity": "danger",
                "message": (
                    f"El area {area_row['name']} presenta la mayor sobre-ejecucion, "
                    f"con una desviacion de {area_row['variance_value']:,.0f}."
                ),
                "criterion": "Area con mayor variacion positiva de ejecutado menos proyectado.",
            }
        )

    executed_months = month_group[month_group["executed"] > 0]
    if len(executed_months) >= 2:
        latest = executed_months.iloc[-1]
        previous = executed_months.iloc[-2]
        delta = float(latest["executed"] - previous["executed"])
        direction = "aumento" if delta > 0 else "disminuyo"
        insights.append(
            {
                "type": "month_over_month",
                "severity": "info",
                "message": (
                    f"El ejecutado de {latest['month_label']} {direction} {abs(delta):,.0f} "
                    f"frente a {previous['month_label']}."
                ),
                "criterion": "Comparacion del ejecutado entre los dos ultimos meses con ejecucion visible.",
            }
        )

    projected_total = max(float(area_group["projected"].sum()), 1.0)
    top3_share = round((float(area_group.head(3)["projected"].sum()) / projected_total) * 100, 2)
    insights.append(
        {
            "type": "budget_concentration",
            "severity": "info",
            "message": f"El {top3_share}% del presupuesto visible se concentra en las 3 areas principales.",
            "criterion": "Suma del proyectado del top 3 de areas / proyectado total visible.",
        }
    )

    top_account = account_group[account_group["variance_value"] > 0].sort_values("variance_value", ascending=False).head(1)
    if not top_account.empty:
        account_row = top_account.iloc[0]
        insights.append(
            {
                "type": "critical_account",
                "severity": "warning",
                "message": (
                    f"La cuenta {account_row['account_name']} es la mas critica por sobre-ejecucion, "
                    f"con un exceso de {account_row['variance_value']:,.0f}."
                ),
                "criterion": "Cuenta hoja con mayor variacion positiva de ejecutado menos proyectado.",
            }
        )

    if summary["over_execution_count"]:
        insights.append(
            {
                "type": "over_execution_count",
                "severity": "warning",
                "message": (
                    f"Hay {summary['over_execution_count']} cuentas hoja con sobre-ejecucion en la vista actual."
                ),
                "criterion": "Conteo de cuentas hoja con ejecutado acumulado mayor al proyectado acumulado.",
            }
        )
    else:
        insights.append(
            {
                "type": "over_execution_count",
                "severity": "positive",
                "message": "No se observan cuentas hoja con sobre-ejecucion en la vista actual.",
                "criterion": "Conteo de cuentas hoja con ejecutado acumulado mayor al proyectado acumulado.",
            }
        )

    return insights[:6]
