from __future__ import annotations

import pandas as pd

from .aggregations import aggregate_by_account, aggregate_by_area


def build_rankings(leaf_df: pd.DataFrame) -> dict:
    if leaf_df.empty:
        return {
            "top_areas": [],
            "top_over_execution": [],
            "top_under_execution": [],
        }

    area_rank = aggregate_by_area(leaf_df)
    account_rank = aggregate_by_account(leaf_df)

    return {
        "top_areas": area_rank.head(5).to_dict(orient="records"),
        "top_over_execution": account_rank[account_rank["variance_value"] > 0]
        .sort_values("variance_value", ascending=False)
        .head(5)
        .to_dict(orient="records"),
        "top_under_execution": account_rank.sort_values("variance_value", ascending=True)
        .head(5)
        .to_dict(orient="records"),
    }
