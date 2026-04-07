from __future__ import annotations


def execution_pct(projected: float, executed: float) -> float:
    if projected <= 0:
        return 100.0 if executed > 0 else 0.0
    return round((executed / projected) * 100, 2)


def variance_pct(projected: float, executed: float) -> float:
    if projected <= 0:
        return 100.0 if executed > 0 else 0.0
    return round(((executed - projected) / projected) * 100, 2)


def budget_status(execution_value: float) -> str:
    if execution_value <= 90:
        return "green"
    if execution_value <= 100:
        return "yellow"
    return "red"
