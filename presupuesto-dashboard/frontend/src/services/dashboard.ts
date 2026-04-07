import {
  AreasResponse,
  DashboardBundle,
  DashboardFilters,
  FiltersResponse,
  HierarchyResponse,
  InsightsResponse,
  RankingsResponse,
  SummaryResponse,
  TrendResponse,
} from "types/budget";

import { apiRequest } from "./api";

function buildQueryString(filters: DashboardFilters): string {
  const params = new URLSearchParams();
  if (filters.months.length) {
    params.set("month", filters.months.join(","));
  }
  if (filters.area) {
    params.set("area", filters.area);
  }
  if (filters.responsible) {
    params.set("responsable", filters.responsible);
  }
  const query = params.toString();
  return query ? `?${query}` : "";
}

export function createQueryKey(filters: DashboardFilters): string {
  return buildQueryString(filters) || "default";
}

export async function fetchFilters(): Promise<FiltersResponse> {
  return apiRequest<FiltersResponse>("/api/budget/filters/");
}

export async function fetchDashboardBundle(filters: DashboardFilters): Promise<DashboardBundle> {
  const query = buildQueryString(filters);
  const [summary, trend, areas, hierarchy, rankings, insights] = await Promise.all([
    apiRequest<SummaryResponse>(`/api/budget/summary/${query}`),
    apiRequest<TrendResponse>(`/api/budget/trend/${query}`),
    apiRequest<AreasResponse>(`/api/budget/areas/${query}`),
    apiRequest<HierarchyResponse>(`/api/budget/hierarchy/${query}`),
    apiRequest<RankingsResponse>(`/api/budget/rankings/${query}`),
    apiRequest<InsightsResponse>(`/api/budget/insights/${query}`),
  ]);

  return { summary, trend, areas, hierarchy, rankings, insights };
}

export async function uploadBudgetFile(file: File): Promise<void> {
  const formData = new FormData();
  formData.append("file", file);
  await apiRequest("/api/budget/upload/", {
    method: "POST",
    body: formData,
  });
}
