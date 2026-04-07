from pathlib import Path

from django.conf import settings
from django.test import TestCase
from rest_framework.test import APIClient

from budget.ingestion.tabular_transform import normalize_excel_source
from budget.models import BudgetDataset
from budget.services.dataset_service import import_fallback_dataset, import_excel_dataset
from budget.services.query_service import get_available_filters


class ExcelNormalizationTests(TestCase):
    def test_normalizes_real_budget_excel(self):
        excel_path = Path(settings.BUDGET_DEFAULT_EXCEL_PATH)
        payload = normalize_excel_source(excel_path.read_bytes(), sheet_name=settings.BUDGET_DEFAULT_SHEET)

        self.assertEqual(payload["sheet_name"], "Gastos y costos detalle")
        self.assertIn("Ene-26", payload["import_stats"]["months"])
        self.assertIn("Dic-26", payload["import_stats"]["months"])
        self.assertFalse(payload["import_stats"]["has_responsible"])
        self.assertGreater(payload["import_stats"]["unique_accounts"], 100)
        self.assertGreater(len(payload["entries"]), 1000)

    def test_variance_column_is_not_used_as_projected(self):
        excel_path = Path(settings.BUDGET_DEFAULT_EXCEL_PATH)
        payload = normalize_excel_source(excel_path.read_bytes(), sheet_name=settings.BUDGET_DEFAULT_SHEET)
        target = next(
            entry
            for entry in payload["entries"]
            if entry["account_code"] == "51151701" and entry["month_key"] == "2026-01"
        )

        self.assertEqual(target["projected"], 0.0)
        self.assertGreater(target["executed"], 0.0)
        self.assertEqual(target["variance_value"], target["executed"])


class BudgetApiTests(TestCase):
    def setUp(self):
        import_fallback_dataset()
        self.client = APIClient(HTTP_HOST="testserver")

    def test_summary_and_filters_endpoints(self):
        summary = self.client.get("/api/budget/summary/")
        filters = self.client.get("/api/budget/filters/")

        self.assertEqual(summary.status_code, 200)
        self.assertEqual(filters.status_code, 200)
        self.assertIn("kpis", summary.json())
        self.assertEqual(summary.json()["context"]["mode"], "consolidated")
        self.assertGreater(len(filters.json()["months"]), 0)

    def test_hierarchy_respects_filters(self):
        response = self.client.get(
            "/api/budget/hierarchy/",
            {"month": "2026-03", "area": "TALENTO HUMANO"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["display_root_level"], 4)
        self.assertGreater(len(payload["roots"]), 0)
        self.assertEqual(payload["roots"][0]["account_code"], "5105")

    def test_upload_replaces_active_dataset(self):
        excel_path = Path(settings.BUDGET_DEFAULT_EXCEL_PATH)
        with excel_path.open("rb") as handle:
            response = self.client.post(
                "/api/budget/upload/",
                {"file": handle},
                format="multipart",
            )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(BudgetDataset.objects.filter(is_active=True).count(), 1)
        self.assertEqual(BudgetDataset.objects.count(), 2)


class FilterNormalizationTests(TestCase):
    def test_area_filter_options_are_unique_after_real_import(self):
        excel_path = Path(settings.BUDGET_DEFAULT_EXCEL_PATH)
        dataset = import_excel_dataset(
            file_bytes=excel_path.read_bytes(),
            filename=excel_path.name,
            sheet_name=settings.BUDGET_DEFAULT_SHEET,
            dataset_name="test-real-import",
        )

        filters = get_available_filters(dataset)

        self.assertEqual(len(filters["areas"]), len(set(filters["areas"])))
        self.assertIn("CARTERA", filters["areas"])
        self.assertIn("GER. ADMON", filters["areas"])
