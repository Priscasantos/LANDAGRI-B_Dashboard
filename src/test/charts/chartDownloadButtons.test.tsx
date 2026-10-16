import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import EChartsBase from '../../components/charts/echarts/EChartsBase';
import { buildLineOption } from '../../components/charts/echarts/echarts-options';
import { ThemeProvider } from '../../components/theme-provider';
import InitiativesTable from '../../components/initiatives/InitiativesTable';
import { useDashboardStore } from '../../stores/dashboardStore';
import type { InitiativeRow } from '../../types/initiative';

function stubAnchorClick(): string[] {
  const downloads: string[] = [];
  vi.stubGlobal('URL', {
    createObjectURL: vi.fn(() => 'blob:mock'),
    revokeObjectURL: vi.fn(() => undefined),
  });
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(function (
    this: HTMLAnchorElement,
  ): void {
    downloads.push(this.download);
  });
  return downloads;
}

function seedTable(): void {
  useDashboardStore.setState({
    initiatives: [
      {
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
        Methodology: 'Machine Learning',
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
      } as InitiativeRow,
    ],
    isLoading: false,
    error: null,
  });
}

describe('chart download buttons (Expansão #2)', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('EChartsBase exporta o dataset visível com nome rota/locale', () => {
    const downloads = stubAnchorClick();
    const option = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    render(
      <ThemeProvider>
        <EChartsBase
          option={option}
          ariaLabel="Evolução"
          chartId="evolucao"
          route="temporal"
          exportRows={[{ ano: 2020, valor: 1 }]}
        />
      </ThemeProvider>,
    );
    const button = screen.getByRole('button', { name: /exportar csv/i });
    fireEvent.click(button);
    expect(downloads).toEqual(['landagri-temporal-pt-br-evolucao.csv']);
  });

  it('EChartsBase omite o botão CSV sem exportRows (toolbox segue no gráfico)', () => {
    const option = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    render(
      <ThemeProvider>
        <EChartsBase option={option} ariaLabel="Evolução" />
      </ThemeProvider>,
    );
    expect(screen.queryByRole('button', { name: /exportar csv|export csv/i })).toBeNull();
    expect(screen.getByRole('img', { name: 'Evolução' })).toBeInTheDocument();
  });

  it('InitiativesTable exporta CSV com nome overview/locale', () => {
    const downloads = stubAnchorClick();
    seedTable();
    render(<InitiativesTable />);
    fireEvent.click(screen.getByRole('button', { name: /exportar csv/i }));
    expect(downloads).toEqual(['landagri-overview-pt-br-initiatives.csv']);
  });
});
