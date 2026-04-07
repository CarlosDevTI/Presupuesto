from __future__ import annotations

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from budget.domain.aggregations import aggregate_by_area, aggregate_monthly
from budget.domain.explainability import build_view_context
from budget.domain.filters import parse_filters
from budget.domain.hierarchy import build_hierarchy
from budget.domain.insights import build_insights
from budget.domain.kpis import build_summary_metrics
from budget.domain.rankings import build_rankings
from budget.models import BudgetDataset
from budget.serializers import DatasetMetadataSerializer, UploadBudgetSerializer
from budget.services.dataset_service import ensure_active_dataset, get_dataset_or_active, import_excel_dataset
from budget.services.query_service import get_available_filters, get_entries_frame


class BudgetBaseView(APIView):
    def get_dataset(self, request):
        ensure_active_dataset()
        dataset_id = request.query_params.get("dataset_id")
        if not dataset_id:
            return get_dataset_or_active(None)
        return get_object_or_404(BudgetDataset, pk=dataset_id)

    def get_frames(self, request):
        dataset = self.get_dataset(request)
        filters = parse_filters(request.query_params)
        all_entries_df = get_entries_frame(dataset, filters, leaf_only=False)
        leaf_df = get_entries_frame(dataset, filters, leaf_only=True)
        filters_meta = get_available_filters(dataset)
        context = build_view_context(filters, filters_meta["months"])
        return dataset, filters, filters_meta, context, all_entries_df, leaf_df


class BudgetUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = UploadBudgetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]
        dataset = import_excel_dataset(
            file_bytes=uploaded_file.read(),
            filename=uploaded_file.name,
            sheet_name=request.data.get("sheet_name"),
            dataset_name=request.data.get("name") or uploaded_file.name,
        )
        return Response(
            DatasetMetadataSerializer(
                {
                    "id": dataset.id,
                    "name": dataset.name,
                    "status": dataset.status,
                    "source_sheet": dataset.source_sheet,
                    "source_file": dataset.source_file,
                    "warnings": dataset.warnings_json,
                    "import_stats": dataset.import_stats,
                    "is_active": dataset.is_active,
                }
            ).data,
            status=status.HTTP_201_CREATED,
        )


class BudgetSummaryView(BudgetBaseView):
    def get(self, request):
        dataset, filters, _, context, _, leaf_df = self.get_frames(request)
        return Response(
            {
                "dataset": _dataset_payload(dataset),
                "filters": filters.__dict__,
                "context": context,
                "kpis": build_summary_metrics(leaf_df),
            }
        )


class BudgetTrendView(BudgetBaseView):
    def get(self, request):
        dataset, _, _, _, _, leaf_df = self.get_frames(request)
        trend = aggregate_monthly(leaf_df).to_dict(orient="records")
        return Response({"dataset": _dataset_payload(dataset), "series": trend})


class BudgetAreasView(BudgetBaseView):
    def get(self, request):
        dataset, _, _, _, _, leaf_df = self.get_frames(request)
        areas = aggregate_by_area(leaf_df).fillna("").to_dict(orient="records")
        return Response({"dataset": _dataset_payload(dataset), "areas": areas})


class BudgetHierarchyView(BudgetBaseView):
    def get(self, request):
        dataset, _, _, context, all_entries_df, leaf_df = self.get_frames(request)
        hierarchy = build_hierarchy(all_entries_df, leaf_df)
        return Response({"dataset": _dataset_payload(dataset), "context": context, **hierarchy})


class BudgetRankingsView(BudgetBaseView):
    def get(self, request):
        dataset, _, _, context, _, leaf_df = self.get_frames(request)
        return Response({"dataset": _dataset_payload(dataset), "context": context, **build_rankings(leaf_df)})


class BudgetInsightsView(BudgetBaseView):
    def get(self, request):
        dataset, _, _, context, _, leaf_df = self.get_frames(request)
        return Response({"dataset": _dataset_payload(dataset), "context": context, "insights": build_insights(leaf_df)})


class BudgetFiltersView(BudgetBaseView):
    def get(self, request):
        dataset = self.get_dataset(request)
        return Response(
            {
                "dataset": _dataset_payload(dataset),
                **get_available_filters(dataset),
            }
        )


def _dataset_payload(dataset) -> dict:
    return {
        "id": dataset.id,
        "name": dataset.name,
        "status": dataset.status,
        "source_sheet": dataset.source_sheet,
        "source_file": dataset.source_file,
        "warnings": dataset.warnings_json,
        "import_stats": dataset.import_stats,
    }
