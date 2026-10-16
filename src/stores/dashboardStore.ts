import { create } from 'zustand';
import type { InitiativeRow, CoverageType, MethodologyType } from '../types/initiative';
import type { ModuleName, PageName } from '../types/theme';

interface FilterState {
  coverageTypes: CoverageType[];
  methodologies: MethodologyType[];
  resolutionRange: [number, number];
  accuracyRange: [number, number];
}

interface UIState {
  sidebarOpen: boolean;
  currentModule: ModuleName;
  currentPage: PageName;
}

interface SelectionState {
  selectedInitiatives: string[];
  selectedInitiative: string | null;
  compareInitiatives: string[];
}

export interface DashboardState {
  // Data
  initiatives: InitiativeRow[];
  rawMetadata: Record<string, unknown>;
  sensors: Record<string, unknown>;
  isLoading: boolean;
  error: string | null;

  // Filters
  filters: FilterState;
  setFilter: (key: keyof FilterState, value: unknown) => void;
  resetFilters: () => void;

  // UI
  ui: UIState;
  setCurrentModule: (module: ModuleName) => void;
  setCurrentPage: (page: PageName) => void;
  toggleSidebar: () => void;

  // Selection
  selection: SelectionState;
  setSelectedInitiative: (name: string | null) => void;
  setCompareInitiatives: (names: string[]) => void;
  toggleSelectedInitiative: (name: string) => void;

  // Data actions
  setInitiatives: (data: InitiativeRow[], raw?: Record<string, unknown>) => void;
  setSensorsData: (sensors: Record<string, unknown>) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;

  // Computed
  getFilteredInitiatives: () => InitiativeRow[];
  getInitiativeByName: (name: string) => InitiativeRow | undefined;
}

export const useDashboardStore = create<DashboardState>((set, get) => ({
  // Initial state
  initiatives: [],
  rawMetadata: {},
  sensors: {},
  isLoading: false,
  error: null,

  filters: {
    coverageTypes: [],
    methodologies: [],
    resolutionRange: [0, 1000],
    accuracyRange: [0, 100],
  },

  ui: {
    sidebarOpen: true,
    currentModule: 'Overview' as ModuleName,
    currentPage: 'Dashboard Overview' as PageName,
  },

  selection: {
    selectedInitiatives: [],
    selectedInitiative: null,
    compareInitiatives: [],
  },

  // Filter actions
  setFilter: (key, value) =>
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    })),

  resetFilters: () =>
    set({
      filters: {
        coverageTypes: [],
        methodologies: [],
        resolutionRange: [0, 1000],
        accuracyRange: [0, 100],
      },
    }),

  // UI actions
  setCurrentModule: (module) =>
    set((state) => ({
      ui: { ...state.ui, currentModule: module },
    })),

  setCurrentPage: (page) =>
    set((state) => ({
      ui: { ...state.ui, currentPage: page },
    })),

  toggleSidebar: () =>
    set((state) => ({
      ui: { ...state.ui, sidebarOpen: !state.ui.sidebarOpen },
    })),

  // Selection actions
  setSelectedInitiative: (name) =>
    set((state) => ({
      selection: { ...state.selection, selectedInitiative: name },
    })),

  setCompareInitiatives: (names) =>
    set((state) => ({
      selection: { ...state.selection, compareInitiatives: names },
    })),

  toggleSelectedInitiative: (name) =>
    set((state) => {
      const current = state.selection.selectedInitiatives;
      const updated = current.includes(name)
        ? current.filter((n) => n !== name)
        : [...current, name];
      return { selection: { ...state.selection, selectedInitiatives: updated } };
    }),

  // Data actions
  setInitiatives: (data, raw = {}) =>
    set({
      initiatives: data,
      rawMetadata: raw,
      isLoading: false,
      error: null,
    }),

  setSensorsData: (sensors) => set({ sensors }),

  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error, isLoading: false }),

  // Computed
  getFilteredInitiatives: () => {
    const { initiatives, filters } = get();
    return initiatives.filter((init) => {
      if (filters.coverageTypes.length > 0 && !filters.coverageTypes.includes(init.Coverage)) return false;
      if (filters.methodologies.length > 0 && !filters.methodologies.includes(init.Methodology)) return false;
      if (init.Resolution < filters.resolutionRange[0] || init.Resolution > filters.resolutionRange[1]) return false;
      if (init.Accuracy < filters.accuracyRange[0] || init.Accuracy > filters.accuracyRange[1]) return false;
      return true;
    });
  },

  getInitiativeByName: (name) => {
    return get().initiatives.find((i) => i.Name === name);
  },
}));
