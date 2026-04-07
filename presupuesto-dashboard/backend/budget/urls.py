from django.urls import path

from .views import (
    BudgetAreasView,
    BudgetFiltersView,
    BudgetHierarchyView,
    BudgetInsightsView,
    BudgetRankingsView,
    BudgetSummaryView,
    BudgetTrendView,
    BudgetUploadView,
)

urlpatterns = [
    path("upload/", BudgetUploadView.as_view(), name="budget-upload"),
    path("summary/", BudgetSummaryView.as_view(), name="budget-summary"),
    path("trend/", BudgetTrendView.as_view(), name="budget-trend"),
    path("areas/", BudgetAreasView.as_view(), name="budget-areas"),
    path("hierarchy/", BudgetHierarchyView.as_view(), name="budget-hierarchy"),
    path("rankings/", BudgetRankingsView.as_view(), name="budget-rankings"),
    path("insights/", BudgetInsightsView.as_view(), name="budget-insights"),
    path("filters/", BudgetFiltersView.as_view(), name="budget-filters"),
]
