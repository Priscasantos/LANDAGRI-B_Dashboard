import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';

import { ThemeProvider } from '../../components/theme-provider';
import AgriculturalCharts from '../../components/overview/AgriculturalCharts';

function renderCharts(): void {
  render(
    <ThemeProvider>
      <AgriculturalCharts />
    </ThemeProvider>,
  );
}

describe('AgriculturalCharts (echarts)', () => {
  it('renders IBGE/CONAB section heading and does not require plotly', async () => {
    renderCharts();
    expect(
      await screen.findByRole('heading', { name: /dados agrícolas brasileiros/i }),
    ).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /evolução da produção/i })).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /distribuição da produção/i })).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /área média colhida/i })).toBeInTheDocument();
  });

  it('charts are keyboard-focusable', async () => {
    renderCharts();
    const chart = await screen.findByRole('img', { name: /evolução da produção/i });
    chart.focus();
    expect(chart).toHaveFocus();
  });

  it('exposes data source note', async () => {
    renderCharts();
    expect(await screen.findByText(/fonte:/i)).toBeInTheDocument();
  });
});
