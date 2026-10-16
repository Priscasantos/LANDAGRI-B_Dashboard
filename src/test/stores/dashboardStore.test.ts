import { describe, it, expect, beforeEach } from 'vitest';
import { useDashboardStore } from '../../stores/dashboardStore';

describe('dashboardStore', () => {
  beforeEach(() => {
    useDashboardStore.setState({
      initiatives: [],
      rawMetadata: {},
      isLoading: false,
      error: null,
    });
  });

  it('should initialize with default state', () => {
    const state = useDashboardStore.getState();
    expect(state.initiatives).toEqual([]);
    expect(state.isLoading).toBe(false);
    expect(state.error).toBeNull();
  });

  it('should set initiatives data', () => {
    const mockData = [{
      Name: 'Test', Display_Name: 'Test', Acronym: 'TST',
      Provider: '', Source: '', Resolution: 30, Resolution_Min: 30, Resolution_Max: 30,
      Available_Years: [2020], Year_Start: 2020, Year_End: 2020, Temporal_Duration: 0,
      Temporal_Frequency: '', Update_Frequency: '', Reference_System: '',
      Methodology: 'Shallow ML' as const, Classification_Method: '', Coverage: 'Global' as const,
      Accuracy: 90, Accuracy_Min: 90, Accuracy_Max: 90, Number_of_Classes: 10,
      Class_Legend: '', Number_of_Agriculture_Classes: 0, Agricultural_Capabilities: '',
      Algorithm: '', Sensors: [], Detailed_Products: [], Has_Detailed_Products: false,
    }];

    useDashboardStore.getState().setInitiatives(mockData, {});
    const state = useDashboardStore.getState();
    expect(state.initiatives).toHaveLength(1);
    expect(state.initiatives[0].Name).toBe('Test');
    expect(state.isLoading).toBe(false);
  });

  it('should set loading state', () => {
    useDashboardStore.getState().setLoading(true);
    expect(useDashboardStore.getState().isLoading).toBe(true);
  });

  it('should set error state', () => {
    useDashboardStore.getState().setError('Test error');
    expect(useDashboardStore.getState().error).toBe('Test error');
    expect(useDashboardStore.getState().isLoading).toBe(false);
  });

  it('should update filters', () => {
    useDashboardStore.getState().setFilter('coverageTypes', ['Global']);
    expect(useDashboardStore.getState().filters.coverageTypes).toEqual(['Global']);
  });

  it('should reset filters', () => {
    useDashboardStore.getState().setFilter('coverageTypes', ['Global']);
    useDashboardStore.getState().resetFilters();
    expect(useDashboardStore.getState().filters.coverageTypes).toEqual([]);
  });

  it('should toggle sidebar', () => {
    const initial = useDashboardStore.getState().ui.sidebarOpen;
    useDashboardStore.getState().toggleSidebar();
    expect(useDashboardStore.getState().ui.sidebarOpen).toBe(!initial);
  });

  it('should select initiative', () => {
    useDashboardStore.getState().setSelectedInitiative('TestInitiative');
    expect(useDashboardStore.getState().selection.selectedInitiative).toBe('TestInitiative');
  });
});
