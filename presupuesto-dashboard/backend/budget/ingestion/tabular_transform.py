from __future__ import annotations

from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from io import BytesIO
from pathlib import Path
from typing import BinaryIO

from .excel_reader import read_workbook_matrix
from .header_normalizer import ColumnSpec, detect_header_layout
from ..domain.normalization import normalize_area_name
from ..domain.status import budget_status, execution_pct, variance_pct

SPANISH_MONTHS = {
    "Ene": 1,
    "Feb": 2,
    "Mar": 3,
    "Abr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Ago": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dic": 12,
}


def normalize_excel_source(
    file_source: str | Path | BinaryIO | bytes,
    sheet_name: str | None = None,
) -> dict:
    workbook_source = BytesIO(file_source) if isinstance(file_source, bytes) else file_source
    selected_sheet, rows = read_workbook_matrix(workbook_source, sheet_name=sheet_name)
    layout = detect_header_layout(selected_sheet, rows)
    data_rows = rows[layout.data_start_index :]
    base_columns = {
        column.base_name: column.index for column in layout.columns if column.kind == "base"
    }
    metric_columns = [column for column in layout.columns if column.kind == "metric"]

    grouped_metrics: dict[str, dict[str, ColumnSpec]] = defaultdict(dict)
    for column in metric_columns:
        grouped_metrics[column.month_label][column.metric] = column

    warnings = list(layout.warnings)
    area_cache: str | None = None
    normalized_entries: list[dict] = []
    source_accounts: list[dict] = []
    mismatch_count = 0

    for row_index, row in enumerate(data_rows, start=layout.data_start_index + 1):
        account_code = _clean_account_code(_get_value(row, base_columns["account_code"]))
        account_name = str(_get_value(row, base_columns["account_name"]) or "").strip()
        level = _to_int(_get_value(row, base_columns["level"]))

        if not account_code or not account_name or level is None:
            continue

        raw_area = normalize_area_name(_get_value(row, base_columns.get("area")), area_cache)
        if raw_area:
            area_cache = raw_area
        area = raw_area or area_cache
        responsible = str(_get_value(row, base_columns.get("responsible")) or "").strip() or None

        source_accounts.append(
            {
                "account_code": account_code,
                "account_name": account_name,
                "area": area,
                "responsible": responsible,
                "level": level,
            }
        )

        for month_label, specs in grouped_metrics.items():
            projected = _to_float(_get_value(row, specs.get("projected").index if specs.get("projected") else None))
            executed = _to_float(_get_value(row, specs.get("executed").index if specs.get("executed") else None))
            provided_variance = _to_float(
                _get_value(row, specs.get("variance").index if specs.get("variance") else None)
            )
            computed_variance = round(executed - projected, 2)
            if specs.get("variance") and abs(provided_variance - computed_variance) > 1:
                mismatch_count += 1

            month_key, month_date = _month_metadata(month_label)
            execution_value = execution_pct(projected, executed)
            normalized_entries.append(
                {
                    "account_code": account_code,
                    "account_name": account_name,
                    "area": area,
                    "responsible": responsible,
                    "level": level,
                    "month_key": month_key,
                    "month_label": month_label,
                    "month_date": month_date,
                    "projected": projected,
                    "executed": executed,
                    "variance_value": computed_variance,
                    "variance_pct": variance_pct(projected, executed),
                    "execution_pct": execution_value,
                    "status": budget_status(execution_value),
                    "source_row": row_index,
                }
            )

    if mismatch_count:
        warnings.append(
            f"Se recalcularon variaciones mensuales en {mismatch_count} celdas inconsistentes."
        )

    is_leaf_map = _detect_leaf_accounts([account["account_code"] for account in source_accounts])
    deduped_entries = _group_duplicate_entries(normalized_entries, is_leaf_map)
    normalized_areas = sorted({entry["area"] for entry in deduped_entries if entry["area"]})

    import_stats = {
        "source_rows": len(data_rows),
        "normalized_entries": len(deduped_entries),
        "unique_accounts": len(is_leaf_map),
        "months": sorted(grouped_metrics.keys(), key=lambda label: _month_metadata(label)[1]),
        "has_responsible": "responsible" in base_columns,
        "header_rows": layout.data_start_index,
        "normalized_areas_count": len(normalized_areas),
    }

    return {
        "sheet_name": selected_sheet,
        "warnings": warnings,
        "import_stats": import_stats,
        "entries": deduped_entries,
        "source_accounts": source_accounts,
        "account_lengths": sorted({len(code) for code in is_leaf_map}),
    }


def _group_duplicate_entries(entries: list[dict], is_leaf_map: dict[str, bool]) -> list[dict]:
    grouped: dict[tuple, dict] = {}
    for entry in entries:
        key = (
            entry["account_code"],
            entry["account_name"],
            entry["area"],
            entry["responsible"],
            entry["level"],
            entry["month_key"],
        )
        if key not in grouped:
            grouped[key] = {**entry}
            grouped[key]["is_leaf"] = is_leaf_map.get(entry["account_code"], False)
            continue

        grouped[key]["projected"] += entry["projected"]
        grouped[key]["executed"] += entry["executed"]
        grouped[key]["variance_value"] += entry["variance_value"]

    results = []
    for entry in grouped.values():
        entry["variance_pct"] = variance_pct(entry["projected"], entry["executed"])
        entry["execution_pct"] = execution_pct(entry["projected"], entry["executed"])
        entry["status"] = budget_status(entry["execution_pct"])
        results.append(entry)

    return sorted(results, key=lambda item: (item["month_key"], item["account_code"]))


def _detect_leaf_accounts(account_codes: list[str]) -> dict[str, bool]:
    unique_codes = sorted(set(account_codes), key=len)
    return {
        code: not any(other.startswith(code) and len(other) > len(code) for other in unique_codes)
        for code in unique_codes
    }


def _clean_account_code(value: object) -> str:
    if value is None:
        return ""
    try:
        decimal_value = Decimal(str(value))
        return format(decimal_value.quantize(Decimal("1")), "f").split(".")[0]
    except (InvalidOperation, ValueError):
        return str(value).strip()


def _month_metadata(month_label: str) -> tuple[str, date]:
    month_name, year_suffix = month_label.split("-")
    month_number = SPANISH_MONTHS[month_name]
    year = 2000 + int(year_suffix)
    month_date = date(year, month_number, 1)
    return month_date.strftime("%Y-%m"), month_date


def _to_float(value: object) -> float:
    try:
        if value is None or str(value).strip() == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _to_int(value: object) -> int | None:
    try:
        if value is None or str(value).strip() == "":
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _get_value(row: list[object], index: int | None) -> object:
    if index is None or index >= len(row):
        return None
    return row[index]
