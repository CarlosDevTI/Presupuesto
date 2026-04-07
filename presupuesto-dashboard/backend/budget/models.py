from django.db import models


class BudgetDataset(models.Model):
    class Status(models.TextChoices):
        READY = "ready", "Ready"
        FALLBACK = "fallback", "Fallback"
        ERROR = "error", "Error"

    name = models.CharField(max_length=160)
    source_sheet = models.CharField(max_length=120, blank=True)
    source_file = models.CharField(max_length=255, blank=True)
    source_hash = models.CharField(max_length=64, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.READY)
    warnings_json = models.JSONField(default=list, blank=True)
    import_stats = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} ({self.status})"


class BudgetEntry(models.Model):
    dataset = models.ForeignKey(
        BudgetDataset,
        related_name="entries",
        on_delete=models.CASCADE,
    )
    account_code = models.CharField(max_length=32, db_index=True)
    account_name = models.CharField(max_length=255)
    area = models.CharField(max_length=160, blank=True, null=True, db_index=True)
    responsible = models.CharField(max_length=160, blank=True, null=True, db_index=True)
    level = models.PositiveSmallIntegerField(db_index=True)
    month_key = models.CharField(max_length=7, db_index=True)
    month_label = models.CharField(max_length=16)
    month_date = models.DateField(db_index=True)
    projected = models.FloatField(default=0)
    executed = models.FloatField(default=0)
    variance_value = models.FloatField(default=0)
    variance_pct = models.FloatField(default=0)
    execution_pct = models.FloatField(default=0)
    is_leaf = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ["month_date", "account_code"]
        indexes = [
            models.Index(fields=["dataset", "month_date"]),
            models.Index(fields=["dataset", "account_code"]),
            models.Index(fields=["dataset", "area"]),
            models.Index(fields=["dataset", "responsible"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "dataset",
                    "account_code",
                    "account_name",
                    "area",
                    "responsible",
                    "level",
                    "month_key",
                ],
                name="budget_entry_unique_row",
            )
        ]

    def __str__(self) -> str:
        return f"{self.account_code} {self.month_label}"
