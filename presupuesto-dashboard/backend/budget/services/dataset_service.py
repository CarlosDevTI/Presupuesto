from __future__ import annotations

import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from budget.ingestion.tabular_transform import normalize_excel_source
from budget.models import BudgetDataset, BudgetEntry


def ensure_active_dataset() -> BudgetDataset:
    active_dataset = BudgetDataset.objects.filter(is_active=True).first()
    if active_dataset:
        return active_dataset

    excel_path = Path(settings.BUDGET_DEFAULT_EXCEL_PATH)
    if excel_path.exists():
        try:
            return import_excel_dataset(
                file_bytes=excel_path.read_bytes(),
                filename=excel_path.name,
                sheet_name=settings.BUDGET_DEFAULT_SHEET,
                dataset_name="Dataset principal",
                status=BudgetDataset.Status.READY,
            )
        except Exception as exc:
            return import_fallback_dataset(
                [f"No fue posible cargar el Excel configurado: {exc}"]
            )

    return import_fallback_dataset(
        ["No se encontro el archivo Excel configurado; se activo el dataset demo."]
    )


def get_dataset_or_active(dataset_id: int | None) -> BudgetDataset:
    if dataset_id:
        return BudgetDataset.objects.get(pk=dataset_id)
    return ensure_active_dataset()


def import_excel_dataset(
    file_bytes: bytes,
    filename: str,
    sheet_name: str | None = None,
    dataset_name: str | None = None,
    status: str = BudgetDataset.Status.READY,
) -> BudgetDataset:
    normalized = normalize_excel_source(file_bytes, sheet_name=sheet_name)
    warnings = normalized["warnings"]
    source_hash = hashlib.sha256(file_bytes).hexdigest()
    metadata = {
        **normalized["import_stats"],
        "account_lengths": normalized["account_lengths"],
    }
    return _persist_dataset(
        name=dataset_name or filename,
        source_sheet=normalized["sheet_name"],
        source_file=filename,
        source_hash=source_hash,
        warnings=warnings,
        import_stats=metadata,
        entries=normalized["entries"],
        status=status,
    )


def import_fallback_dataset(extra_warnings: list[str] | None = None) -> BudgetDataset:
    fixture_path = Path(settings.BUDGET_FALLBACK_FIXTURE)
    payload = json.loads(fixture_path.read_text(encoding="utf-8-sig"))
    warnings = list(payload.get("warnings", []))
    if extra_warnings:
        warnings = extra_warnings + warnings
    return _persist_dataset(
        name=payload["name"],
        source_sheet=payload.get("source_sheet", ""),
        source_file=fixture_path.name,
        source_hash=hashlib.sha256(fixture_path.read_bytes()).hexdigest(),
        warnings=warnings,
        import_stats=payload.get("import_stats", {}),
        entries=payload["entries"],
        status=BudgetDataset.Status.FALLBACK,
    )


@transaction.atomic
def _persist_dataset(
    *,
    name: str,
    source_sheet: str,
    source_file: str,
    source_hash: str,
    warnings: list[str],
    import_stats: dict,
    entries: list[dict],
    status: str,
) -> BudgetDataset:
    BudgetDataset.objects.filter(is_active=True).update(is_active=False)
    dataset = BudgetDataset.objects.create(
        name=name,
        source_sheet=source_sheet,
        source_file=source_file,
        source_hash=source_hash,
        warnings_json=warnings,
        import_stats=import_stats,
        status=status,
        is_active=True,
        activated_at=timezone.now(),
    )
    BudgetEntry.objects.bulk_create(
        [
            BudgetEntry(
                dataset=dataset,
                account_code=entry["account_code"],
                account_name=entry["account_name"],
                area=entry["area"],
                responsible=entry["responsible"],
                level=entry["level"],
                month_key=entry["month_key"],
                month_label=entry["month_label"],
                month_date=entry["month_date"],
                projected=entry["projected"],
                executed=entry["executed"],
                variance_value=entry["variance_value"],
                variance_pct=entry["variance_pct"],
                execution_pct=entry["execution_pct"],
                is_leaf=entry["is_leaf"],
            )
            for entry in entries
        ],
        batch_size=1000,
    )
    return dataset

