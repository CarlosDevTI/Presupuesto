from django.contrib import admin

from .models import BudgetDataset, BudgetEntry


@admin.register(BudgetDataset)
class BudgetDatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "status", "source_sheet", "is_active", "created_at")
    list_filter = ("status", "is_active", "source_sheet")
    search_fields = ("name", "source_file", "source_hash")


@admin.register(BudgetEntry)
class BudgetEntryAdmin(admin.ModelAdmin):
    list_display = (
        "account_code",
        "account_name",
        "month_label",
        "area",
        "projected",
        "executed",
        "is_leaf",
    )
    list_filter = ("month_label", "area", "is_leaf", "dataset")
    search_fields = ("account_code", "account_name", "area")
