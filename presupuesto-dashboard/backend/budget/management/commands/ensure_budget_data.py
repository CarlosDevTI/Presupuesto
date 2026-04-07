from django.core.management.base import BaseCommand

from budget.services.dataset_service import ensure_active_dataset


class Command(BaseCommand):
    help = "Garantiza que exista un dataset activo antes de iniciar el servicio."

    def handle(self, *args, **options):
        dataset = ensure_active_dataset()
        self.stdout.write(self.style.SUCCESS(f"Dataset activo listo: {dataset.id}"))