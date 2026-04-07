from __future__ import annotations

from dataclasses import dataclass

from django.http import QueryDict


@dataclass
class FilterParams:
    months: list[str]
    area: str | None
    responsible: str | None


def parse_filters(params: QueryDict | dict) -> FilterParams:
    month_value = params.get("month", "")
    months = [month.strip() for month in month_value.split(",") if month.strip()]
    return FilterParams(
        months=months,
        area=_clean_optional(params.get("area")),
        responsible=_clean_optional(params.get("responsable") or params.get("responsible")),
    )


def _clean_optional(value: str | None) -> str | None:
    if not value:
        return None
    value = value.strip()
    return value or None
