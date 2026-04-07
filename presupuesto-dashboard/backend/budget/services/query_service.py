from __future__ import annotations

import pandas as pd

from budget.domain.filters import FilterParams
from budget.models import BudgetDataset, BudgetEntry

ENTRY_FIELDS = [
    "account_code",
    "account_name",
    "area",
    "responsible",
    "level",
    "month_key",
    "month_label",
    "month_date",
    "projected",
    "executed",
    "variance_value",
    "variance_pct",
    "execution_pct",
    "is_leaf",
]


def get_filtered_queryset(
    dataset: BudgetDataset,
    filters: FilterParams,
    *,
    leaf_only: bool = False,
):
    queryset = BudgetEntry.objects.filter(dataset=dataset)
    if leaf_only:
        queryset = queryset.filter(is_leaf=True)
    if filters.months:
        queryset = queryset.filter(month_key__in=filters.months)
    if filters.area:
        queryset = queryset.filter(area=filters.area)
    if filters.responsible:
        queryset = queryset.filter(responsible=filters.responsible)
    return queryset


def get_entries_frame(
    dataset: BudgetDataset,
    filters: FilterParams,
    *,
    leaf_only: bool = False,
) -> pd.DataFrame:
    values = list(get_filtered_queryset(dataset, filters, leaf_only=leaf_only).values(*ENTRY_FIELDS))
    if not values:
        return pd.DataFrame(columns=ENTRY_FIELDS)
    frame = pd.DataFrame(values)
    frame["month_date"] = pd.to_datetime(frame["month_date"])
    return frame


def get_available_filters(dataset: BudgetDataset) -> dict:
    base_queryset = BudgetEntry.objects.filter(dataset=dataset)
    months = list(
        base_queryset.order_by()
        .values("month_key", "month_label", "month_date")
        .distinct()
        .order_by("month_date")
    )
    areas = list(
        base_queryset.order_by()
        .exclude(area__isnull=True)
        .exclude(area="")
        .values_list("area", flat=True)
        .distinct()
    )
    responsibles = list(
        base_queryset.order_by()
        .exclude(responsible__isnull=True)
        .exclude(responsible="")
        .values_list("responsible", flat=True)
        .distinct()
    )
    return {
        "months": months,
        "areas": sorted(areas),
        "responsibles": sorted(responsibles),
        "has_responsible": bool(responsibles),
    }
