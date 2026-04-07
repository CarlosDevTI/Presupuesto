from __future__ import annotations

import pandas as pd

from .aggregations import aggregate_by_account
from .status import budget_status, execution_pct, variance_pct


def build_summary_metrics(leaf_df: pd.DataFrame) -> dict:
    projected = float(leaf_df["projected"].sum()) if not leaf_df.empty else 0.0
    executed = float(leaf_df["executed"].sum()) if not leaf_df.empty else 0.0
    variance_value = round(executed - projected, 2)
    execution_value = execution_pct(projected, executed)
    variance_value_pct = variance_pct(projected, executed)

    account_summary = aggregate_by_account(leaf_df)
    over_execution_count = int((account_summary["executed"] > account_summary["projected"]).sum())

    return {
        "projected_total": projected,
        "executed_total": executed,
        "execution_pct": execution_value,
        "variance_value": variance_value,
        "variance_pct": variance_value_pct,
        "over_execution_count": over_execution_count,
        "status": budget_status(execution_value),
    }
