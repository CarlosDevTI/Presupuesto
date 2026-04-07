from __future__ import annotations

import pandas as pd

from .rollup import build_children_map, build_parent_map, roll_up_leaf_metrics
from .status import budget_status, execution_pct, variance_pct


def build_hierarchy(all_entries_df: pd.DataFrame, leaf_df: pd.DataFrame) -> dict:
    if all_entries_df.empty:
        return {"roots": [], "display_root_level": None}

    account_meta = (
        all_entries_df.sort_values("level")
        .drop_duplicates(subset=["account_code"])[
            [
                "account_code",
                "account_name",
                "level",
                "area",
                "responsible",
                "is_leaf",
            ]
        ]
    )
    account_codes = account_meta["account_code"].tolist()
    display_root_level = _resolve_display_root_level(account_meta)

    leaf_grouped = leaf_df.groupby("account_code")[["projected", "executed"]].sum().reset_index()
    leaf_metrics = {
        row["account_code"]: {
            "projected": float(row["projected"]),
            "executed": float(row["executed"]),
            "variance_value": float(row["executed"] - row["projected"]),
        }
        for _, row in leaf_grouped.iterrows()
    }
    rolled_up = roll_up_leaf_metrics(account_codes, leaf_metrics)
    parent_map = build_parent_map(account_codes)
    children_map = build_children_map(account_codes)

    node_map: dict[str, dict] = {}
    for record in account_meta.to_dict(orient="records"):
        metrics = rolled_up.get(
            record["account_code"],
            {"projected": 0.0, "executed": 0.0, "variance_value": 0.0},
        )
        projected = round(metrics["projected"], 2)
        executed = round(metrics["executed"], 2)
        variance_value = round(metrics["variance_value"], 2)
        exec_pct = execution_pct(projected, executed)
        node_map[record["account_code"]] = {
            "id": record["account_code"],
            "account_code": record["account_code"],
            "account_name": record["account_name"],
            "level": int(record["level"]),
            "area": record["area"],
            "responsible": record["responsible"],
            "projected": projected,
            "executed": executed,
            "variance_value": variance_value,
            "variance_pct": variance_pct(projected, executed),
            "execution_pct": exec_pct,
            "status": budget_status(exec_pct),
            "is_leaf": bool(record["is_leaf"]),
            "children": [],
        }

    for parent, children in children_map.items():
        if parent is None:
            continue
        node_map[parent]["children"] = [
            node_map[child] for child in children if _has_visible_values(node_map[child])
        ]

    roots = []
    for code, node in node_map.items():
        parent = parent_map.get(code)
        if node["level"] < display_root_level:
            continue
        if parent is None or node_map[parent]["level"] < display_root_level:
            if _has_visible_values(node):
                roots.append(node)

    roots.sort(key=lambda node: node["account_code"])
    return {"roots": roots, "display_root_level": display_root_level}


def _resolve_display_root_level(account_meta: pd.DataFrame) -> int:
    level_candidates = sorted(level for level in account_meta["level"].unique().tolist() if level >= 4)
    return level_candidates[0] if level_candidates else int(account_meta["level"].min())


def _has_visible_values(node: dict) -> bool:
    return bool(node["children"]) or abs(node["projected"]) > 0 or abs(node["executed"]) > 0
