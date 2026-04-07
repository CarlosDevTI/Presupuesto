from __future__ import annotations

import pandas as pd

from .status import execution_pct, variance_pct


def aggregate_monthly(leaf_df: pd.DataFrame) -> pd.DataFrame:
    if leaf_df.empty:
        return pd.DataFrame(columns=["month_key", "month_label", "month_date", "projected", "executed", "variance_value", "execution_pct"])

    grouped = (
        leaf_df.groupby(["month_key", "month_label", "month_date"], dropna=False)[["projected", "executed"]]
        .sum()
        .reset_index()
        .sort_values("month_date")
    )
    grouped["variance_value"] = grouped["executed"] - grouped["projected"]
    grouped["execution_pct"] = grouped.apply(
        lambda row: execution_pct(float(row["projected"]), float(row["executed"])),
        axis=1,
    )
    return grouped


def aggregate_by_area(leaf_df: pd.DataFrame) -> pd.DataFrame:
    if leaf_df.empty:
        return pd.DataFrame(columns=["name", "projected", "executed", "variance_value", "execution_pct", "share_pct"])

    prepared = leaf_df.copy()
    prepared["area_display"] = prepared["area"].fillna("SIN AREA").replace("", "SIN AREA")
    grouped = (
        prepared.groupby("area_display", dropna=False)[["projected", "executed"]]
        .sum()
        .reset_index()
        .rename(columns={"area_display": "name"})
    )
    grouped["variance_value"] = grouped["executed"] - grouped["projected"]
    grouped["execution_pct"] = grouped.apply(
        lambda row: execution_pct(float(row["projected"]), float(row["executed"])),
        axis=1,
    )
    total_projected = max(float(grouped["projected"].sum()), 1.0)
    grouped["share_pct"] = round((grouped["projected"] / total_projected) * 100, 2)
    return grouped.sort_values(["projected", "executed"], ascending=False).reset_index(drop=True)


def aggregate_by_account(leaf_df: pd.DataFrame) -> pd.DataFrame:
    if leaf_df.empty:
        return pd.DataFrame(columns=["account_code", "account_name", "projected", "executed", "variance_value", "variance_pct", "execution_pct"])

    grouped = (
        leaf_df.groupby(["account_code", "account_name"], dropna=False)[["projected", "executed"]]
        .sum()
        .reset_index()
    )
    grouped["variance_value"] = grouped["executed"] - grouped["projected"]
    grouped["variance_pct"] = grouped.apply(
        lambda row: variance_pct(float(row["projected"]), float(row["executed"])),
        axis=1,
    )
    grouped["execution_pct"] = grouped.apply(
        lambda row: execution_pct(float(row["projected"]), float(row["executed"])),
        axis=1,
    )
    return grouped
