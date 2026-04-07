from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

MONTH_PATTERN = re.compile(r"^(ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic)-\d{2}$", re.IGNORECASE)
# Variacion debe evaluarse primero porque el texto real contiene la palabra "proyectado".
METRIC_ALIASES = {
    "variance": ("variacion",),
    "executed": ("ejecutado",),
    "projected": ("proyectado",),
}
BASE_ALIASES = {
    "level": ("nivel",),
    "area": ("area",),
    "account_code": ("cuenta",),
    "account_name": ("concepto",),
    "responsible": ("responsable",),
}
IGNORE_KEYWORDS = (
    "acumulado",
    "presupuesto marzo",
    "total ejecutado",
)


@dataclass
class ColumnSpec:
    index: int
    source_name: str
    kind: str
    base_name: str | None = None
    month_label: str | None = None
    metric: str | None = None


@dataclass
class HeaderLayout:
    sheet_name: str
    data_start_index: int
    columns: list[ColumnSpec]
    warnings: list[str]


def normalize_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"\s+", " ", text).strip().lower()


def detect_header_layout(sheet_name: str, rows: list[list[object]]) -> HeaderLayout:
    data_start_index = _find_data_start_index(rows)
    header_rows = rows[:data_start_index]
    max_columns = max((len(row) for row in rows), default=0)
    warnings: list[str] = []
    current_month = ""
    columns: list[ColumnSpec] = []

    for index in range(max_columns):
        header_cells = [normalize_text(row[index]) if index < len(row) else "" for row in header_rows]
        flattened = " ".join(part for part in header_cells if part).strip()

        if any(keyword in flattened for keyword in IGNORE_KEYWORDS):
            columns.append(ColumnSpec(index=index, source_name=flattened or f"column_{index}", kind="ignore"))
            continue

        base_name = _detect_base_name(header_cells)
        if base_name:
            columns.append(
                ColumnSpec(
                    index=index,
                    source_name=flattened or base_name,
                    kind="base",
                    base_name=base_name,
                )
            )
            continue

        month_candidate = _detect_month_label(header_cells)
        if month_candidate:
            current_month = month_candidate

        metric = _detect_metric(header_cells)
        if metric and current_month:
            columns.append(
                ColumnSpec(
                    index=index,
                    source_name=flattened or f"{current_month} {metric}",
                    kind="metric",
                    month_label=current_month,
                    metric=metric,
                )
            )
            continue

        columns.append(ColumnSpec(index=index, source_name=flattened or f"column_{index}", kind="ignore"))

    found_base_names = {column.base_name for column in columns if column.base_name}
    missing = {"level", "account_code", "account_name"} - found_base_names
    if missing:
        raise ValueError(
            f"No se pudieron detectar columnas base obligatorias: {', '.join(sorted(missing))}."
        )

    if not any(column.kind == "metric" for column in columns):
        raise ValueError("No se detectaron columnas mensuales validas en el Excel.")

    if data_start_index > 2:
        warnings.append(
            f"Se detectaron {data_start_index} filas de encabezado; se normalizaron automaticamente."
        )

    return HeaderLayout(
        sheet_name=sheet_name,
        data_start_index=data_start_index,
        columns=columns,
        warnings=warnings,
    )


def _find_data_start_index(rows: list[list[object]]) -> int:
    for index, row in enumerate(rows):
        if _looks_like_data_row(row):
            return index
    raise ValueError("No se encontro una fila de inicio de datos en la hoja seleccionada.")


def _looks_like_data_row(row: list[object]) -> bool:
    if not row:
        return False
    return _is_number(row[0]) and len(row) > 2 and _is_number(row[2])


def _detect_base_name(header_cells: list[str]) -> str | None:
    for candidate, aliases in BASE_ALIASES.items():
        if any(any(alias == cell for alias in aliases) for cell in header_cells):
            return candidate
    return None


def _detect_month_label(header_cells: list[str]) -> str | None:
    for cell in reversed(header_cells):
        if MONTH_PATTERN.match(cell):
            return cell.title()
    return None


def _detect_metric(header_cells: list[str]) -> str | None:
    merged = " ".join(header_cells)
    for metric, aliases in METRIC_ALIASES.items():
        if any(alias in merged for alias in aliases):
            return metric
    return None


def _is_number(value: object) -> bool:
    try:
        if value is None or str(value).strip() == "":
            return False
        float(value)
        return True
    except (TypeError, ValueError):
        return False
