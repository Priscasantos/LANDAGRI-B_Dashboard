import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ThemeProvider } from '../../components/theme-provider';
import ProductivitySeriesChart from '../../components/agricultural-analysis/AgricultureOverview/ProductivitySeriesChart';
import ProductionValueChart from '../../components/agricultural-analysis/AgricultureOverview/ProductionValueChart';
import SeasonCloseChart from '../../components/agricultural-analysis/AgricultureOverview/SeasonCloseChart';
import ConabEstimatesTab from '../../components/agricultural-analysis/AgricultureOverview/ConabEstimatesTab';
import IbgeEstimatesTab from '../../components/agricultural-analysis/AgricultureOverview/IbgeEstimatesTab';
import MethodologyDistributionTab from '../../components/initiative-analysis/ComparativeAnalysis/MethodologyDistributionTab';
import { useDashboardStore } from '../../stores/dashboardStore';

function renderWithProviders(ui: React.ReactElement): void {
  // Sem LanguageProvider: contexto default = pt-BR (padrão dos testes de charts).
  render(<ThemeProvider>{ui}</ThemeProvider>);
}

beforeEach(() => {
  useDashboardStore.setState({ initiatives: [] });
});

describe('P2b charts (criar)', () => {
  it('ProductivitySeriesChart renders PAM yield heading + line chart', async () => {
    renderWithProviders(<ProductivitySeriesChart />);
    expect(await screen.findByRole('heading', { name: /rendimento médio por cultura/i })).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /rendimento médio/i })).toBeInTheDocument();
  });

  it('ProductionValueChart renders R$ 927 bi KPI + top bar', async () => {
    renderWithProviders(<ProductionValueChart />);
    expect(await screen.findByText(/R\$ 927 bi/)).toBeInTheDocument();
    expect(
      await screen.findByRole('heading', { name: /top culturas por quantidade/i }),
    ).toBeInTheDocument();
  });

  it('SeasonCloseChart renders grouped bar + delta % table', async () => {
    renderWithProviders(<SeasonCloseChart />);
    const headings = await screen.findAllByRole('heading', { name: /fechamento da safra/i });
    expect(headings.length).toBeGreaterThanOrEqual(1);
    const table = await screen.findByRole('table');
    expect(table.textContent).toMatch(/%/);
    expect(table.textContent).toMatch(/2024\/25/);
  });

  it('ConabEstimatesTab keeps line+bar, drops pie por safra', async () => {
    renderWithProviders(<ConabEstimatesTab />);
    expect(await screen.findByRole('heading', { name: /evolução da produção/i })).toBeInTheDocument();
    expect(
      await screen.findByRole('heading', { name: /produtividade por cultura/i }),
    ).toBeInTheDocument();
    expect(screen.queryByText(/distribuição da área plantada/i)).not.toBeInTheDocument();
    const closeHeadings = await screen.findAllByRole('heading', { name: /fechamento da safra/i });
    expect(closeHeadings.length).toBe(2);
  });

  it('IbgeEstimatesTab drops regional sub-tab, keeps PAM value + yield', async () => {
    renderWithProviders(<IbgeEstimatesTab />);
    expect(screen.queryByText(/distribuição regional/i)).not.toBeInTheDocument();
    expect(await screen.findByText(/R\$ 927 bi/)).toBeInTheDocument();
  });
});

describe('P2b MethodologyDistributionTab vira tabela', () => {
  it('renders methodology counts table instead of grouped bar', async () => {
    useDashboardStore.setState({
      initiatives: [
        {
          Name: 'MB',
          Display_Name: 'MapBiomas',
          Methodology: 'Hybrid',
          Coverage: 'National',
        },
        {
          Name: 'TI',
          Display_Name: 'TerraClass',
          Methodology: 'Visual',
          Coverage: 'Regional',
        },
      ] as never,
    });
    renderWithProviders(<MethodologyDistributionTab />);
    expect(await screen.findByRole('table')).toBeInTheDocument();
    // P3: células e cabeçalhos via glossário (locale default pt-BR).
    expect(await screen.findByText('Híbrida')).toBeInTheDocument();
    expect(await screen.findByText('Nacional')).toBeInTheDocument();
    expect(await screen.findByText('Metodologia')).toBeInTheDocument();
  });
});
