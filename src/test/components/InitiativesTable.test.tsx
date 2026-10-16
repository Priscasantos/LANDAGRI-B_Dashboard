import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import InitiativesTable from '../../components/initiatives/InitiativesTable';
import { useDashboardStore } from '../../stores/dashboardStore';
import type { InitiativeRow } from '../../types/initiative';

function row(overrides: Partial<InitiativeRow> = {}): InitiativeRow {
  return {
    Name: 'Test Initiative',
    Display_Name: 'Test Initiative (TST)',
    Acronym: 'TST',
    Provider: 'Test Provider',
    Source: 'Test Source',
    Resolution: 30,
    Resolution_Min: 30,
    Resolution_Max: 30,
    Available_Years: [2020, 2021],
    Year_Start: 2020,
    Year_End: 2021,
    Temporal_Duration: 1,
    Temporal_Frequency: 'Annual',
    Update_Frequency: 'Yearly',
    Reference_System: 'EPSG:4326',
    Methodology: 'Shallow ML',
    Classification_Method: 'RF',
    Coverage: 'National',
    Accuracy: 90,
    Accuracy_Min: 88,
    Accuracy_Max: 92,
    Number_of_Classes: 10,
    Class_Legend: '',
    Number_of_Agriculture_Classes: 2,
    Agricultural_Capabilities: '',
    Algorithm: '',
    Sensors: [],
    Detailed_Products: [],
    Has_Detailed_Products: false,
    ...overrides,
  } as InitiativeRow;
}

function seed(rows: InitiativeRow[]): void {
  useDashboardStore.setState({ initiatives: rows, isLoading: false, error: null });
}

describe('InitiativesTable (Fase 2: iniciativa/área/ano)', () => {
  it('renders iniciativa/área/ano columns', () => {
    seed([row()]);
    render(<InitiativesTable />);
    expect(screen.getByRole('columnheader', { name: /iniciativa/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /área|cobertura/i })).toBeInTheDocument();
    expect(screen.getByRole('columnheader', { name: /ano|período/i })).toBeInTheDocument();
    expect(screen.getByText('Test Initiative (TST)')).toBeInTheDocument();
  });

  it('filters by search text', () => {
    seed([
      row(),
      row({ Name: 'Other', Display_Name: 'Other (OTH)', Acronym: 'OTH' }),
    ]);
    render(<InitiativesTable />);
    fireEvent.change(screen.getByPlaceholderText(/buscar|search/i), { target: { value: 'Other' } });
    expect(screen.getByText('Other (OTH)')).toBeInTheDocument();
    expect(screen.queryByText('Test Initiative (TST)')).not.toBeInTheDocument();
  });

  it('sorts by iniciativa when the header is activated', () => {
    seed([
      row({ Name: 'Zulu', Display_Name: 'Zulu (Z)', Acronym: 'Z' }),
      row({ Name: 'Alpha', Display_Name: 'Alpha (A)', Acronym: 'A' }),
    ]);
    render(<InitiativesTable />);
    fireEvent.click(screen.getByRole('columnheader', { name: /iniciativa/i }));
    const cells = screen.getAllByRole('cell');
    expect(cells[0].textContent).toContain('Alpha');
  });

  it('renders empty state when the store has no initiatives', () => {
    seed([]);
    render(<InitiativesTable />);
    expect(screen.getByText(/nenhuma iniciativa/i)).toBeInTheDocument();
  });
});
