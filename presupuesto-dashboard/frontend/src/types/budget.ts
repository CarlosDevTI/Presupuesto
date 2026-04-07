export type StatusTone = "green" | "yellow" | "red";

export interface DatasetMeta {
  id: number;
  name: string;
  status: string;
  source_sheet: string;
  source_file: string;
  warnings: string[];
  import_stats: Record<string, unknown>;
}

export interface DashboardFilters {
  months: string[];
  area?: string;
  responsible?: string;
}

export interface ViewContext {
  mode: "consolidated" | "filtered";
  label: string;
  basis: {
    months: string;
    areas: string;
    responsibles: string;
    accounts: string;
    double_count_prevention: string;
  };
  kpi_formulas: Array<{
    key: string;
    label: string;
    formula: string;
  }>;
  insight_criteria: Array<{
    type: string;
    criterion: string;
  }>;
}

export interface SummaryResponse {
  dataset: DatasetMeta;
  filters: Record<string, unknown>;
  context: ViewContext;
  kpis: {
    projected_total: number;
    executed_total: number;
    execution_pct: number;
    variance_value: number;
    variance_pct: number;
    over_execution_count: number;
    status: StatusTone;
  };
}

export interface TrendPoint {
  month_key: string;
  month_label: string;
  month_date: string;
  projected: number;
  executed: number;
  variance_value: number;
}

export interface TrendResponse {
  dataset: DatasetMeta;
  series: TrendPoint[];
}

export interface AreaPoint {
  name: string;
  projected: number;
  executed: number;
  variance_value: number;
  execution_pct: number;
  share_pct: number;
}

export interface AreasResponse {
  dataset: DatasetMeta;
  areas: AreaPoint[];
}

export interface HierarchyNode {
  id: string;
  account_code: string;
  account_name: string;
  level: number;
  area?: string | null;
  responsible?: string | null;
  projected: number;
  executed: number;
  variance_value: number;
  variance_pct: number;
  execution_pct: number;
  status: StatusTone;
  is_leaf: boolean;
  children: HierarchyNode[];
}

export interface HierarchyResponse {
  dataset: DatasetMeta;
  context: ViewContext;
  display_root_level: number | null;
  roots: HierarchyNode[];
}

export interface RankingItem {
  name?: string;
  area?: string;
  account_code?: string;
  account_name?: string;
  projected: number;
  executed: number;
  variance_value: number;
  execution_pct?: number;
  variance_pct?: number;
}

export interface RankingsResponse {
  dataset: DatasetMeta;
  context: ViewContext;
  top_areas: RankingItem[];
  top_over_execution: RankingItem[];
  top_under_execution: RankingItem[];
}

export interface InsightItem {
  type: string;
  severity: string;
  message: string;
  criterion: string;
}

export interface InsightsResponse {
  dataset: DatasetMeta;
  context: ViewContext;
  insights: InsightItem[];
}

export interface FilterMonthOption {
  month_key: string;
  month_label: string;
  month_date: string;
}

export interface FiltersResponse {
  dataset: DatasetMeta;
  months: FilterMonthOption[];
  areas: string[];
  responsibles: string[];
  has_responsible: boolean;
}

export interface DashboardBundle {
  summary: SummaryResponse;
  trend: TrendResponse;
  areas: AreasResponse;
  hierarchy: HierarchyResponse;
  rankings: RankingsResponse;
  insights: InsightsResponse;
}
