from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from budget.services.dataset_service import import_excel_dataset, import_fallback_dataset


class Command(BaseCommand):
    help = "Carga el Excel presupuestal o activa el dataset fallback."

    def add_arguments(self, parser):
        parser.add_argument("--file", dest="file_path")
        parser.add_argument("--sheet", dest="sheet_name")
        parser.add_argument("--fallback", action="store_true")

    def handle(self, *args, **options):
        if options["fallback"]:
            dataset = import_fallback_dataset()
            self.stdout.write(self.style.SUCCESS(f"Dataset fallback activado: {dataset.id}"))
            return

        file_path = options["file_path"] or settings.BUDGET_DEFAULT_EXCEL_PATH
        path = Path(file_path)
        if not path.exists():
            raise CommandError(f"No existe el archivo: {path}")

        dataset = import_excel_dataset(
            file_bytes=path.read_bytes(),
            filename=path.name,
            sheet_name=options["sheet_name"] or settings.BUDGET_DEFAULT_SHEET,
            dataset_name=path.stem,
        )
        self.stdout.write(self.style.SUCCESS(f"Dataset cargado correctamente: {dataset.id}"))
