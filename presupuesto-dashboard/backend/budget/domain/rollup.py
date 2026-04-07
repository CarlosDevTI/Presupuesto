from __future__ import annotations

from collections import defaultdict


def build_parent_map(account_codes: list[str]) -> dict[str, str | None]:
    ordered = sorted(set(account_codes), key=lambda code: (len(code), code))
    parents: dict[str, str | None] = {}
    for code in ordered:
        candidates = [other for other in ordered if len(other) < len(code) and code.startswith(other)]
        parents[code] = max(candidates, key=len) if candidates else None
    return parents


def roll_up_leaf_metrics(
    account_codes: list[str],
    leaf_metrics: dict[str, dict[str, float]],
) -> dict[str, dict[str, float]]:
    parent_map = build_parent_map(account_codes)
    rolled_up = {
        code: {
            "projected": 0.0,
            "executed": 0.0,
            "variance_value": 0.0,
        }
        for code in account_codes
    }

    for leaf_code, metrics in leaf_metrics.items():
        cursor = leaf_code
        while cursor:
            rolled_up[cursor]["projected"] += metrics["projected"]
            rolled_up[cursor]["executed"] += metrics["executed"]
            rolled_up[cursor]["variance_value"] += metrics["variance_value"]
            cursor = parent_map.get(cursor)

    return rolled_up


def build_children_map(account_codes: list[str]) -> dict[str | None, list[str]]:
    parent_map = build_parent_map(account_codes)
    children: dict[str | None, list[str]] = defaultdict(list)
    for code, parent in parent_map.items():
        children[parent].append(code)
    for codes in children.values():
        codes.sort()
    return children
