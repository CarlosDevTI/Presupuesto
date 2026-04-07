import { create } from "zustand";

import { createQueryKey, fetchDashboardBundle, fetchFilters, uploadBudgetFile } from "services/dashboard";
import { DashboardBundle, DashboardFilters, FiltersResponse } from "types/budget";

interface DashboardState {
  filters: DashboardFilters;
  filtersMeta?: FiltersResponse;
  dashboard?: DashboardBundle;
  cache: Record<string, DashboardBundle>;
  loading: boolean;
  uploading: boolean;
  error?: string;
  initialize: () => Promise<void>;
  loadDashboard: (force?: boolean) => Promise<void>;
  setFilters: (partial: Partial<DashboardFilters>) => void;
  clearFilters: () => void;
  uploadFile: (file: File) => Promise<void>;
}

const defaultFilters: DashboardFilters = {
  months: [],
};

export const useDashboardStore = create<DashboardState>((set, get) => ({
  filters: defaultFilters,
  cache: {},
  loading: false,
  uploading: false,
  async initialize() {
    const filtersMeta = await fetchFilters();
    set({ filtersMeta });
    await get().loadDashboard(true);
  },
  async loadDashboard(force = false) {
    const { filters, cache } = get();
    const queryKey = createQueryKey(filters);
    if (!force && cache[queryKey]) {
      set({ dashboard: cache[queryKey], error: undefined });
      return;
    }

    set({ loading: true, error: undefined });
    try {
      const dashboard = await fetchDashboardBundle(filters);
      set((state) => ({
        dashboard,
        cache: { ...state.cache, [queryKey]: dashboard },
        loading: false,
      }));
    } catch (error) {
      set({
        loading: false,
        error: error instanceof Error ? error.message : "No fue posible cargar el dashboard.",
      });
    }
  },
  setFilters(partial) {
    set((state) => ({
      filters: {
        ...state.filters,
        ...partial,
      },
    }));
  },
  clearFilters() {
    set({ filters: defaultFilters });
  },
  async uploadFile(file) {
    set({ uploading: true, error: undefined });
    try {
      await uploadBudgetFile(file);
      const filtersMeta = await fetchFilters();
      set({
        filtersMeta,
        filters: defaultFilters,
        cache: {},
        uploading: false,
      });
      await get().loadDashboard(true);
    } catch (error) {
      set({
        uploading: false,
        error: error instanceof Error ? error.message : "No fue posible cargar el archivo.",
      });
    }
  },
}));
