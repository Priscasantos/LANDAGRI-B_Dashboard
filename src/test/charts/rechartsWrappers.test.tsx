import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

// jsdom has no layout — ResponsiveContainer needs a size. Mock it to a
// fixed-size container so recharts renders SVG deterministically.
vi.mock('recharts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('recharts')>();
  const React = await import('react');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactElement }) =>
      React.cloneElement(
        children as React.ReactElement<{ width?: number; height?: number }>,
        { width: 600, height: 350 },
      ),
  };
});

import { RechartsLineChart } from '../../components/charts/recharts/RechartsLineChart';
import { RechartsBarChart } from '../../components/charts/recharts/RechartsBarChart';
import { RechartsAreaChart } from '../../components/charts/recharts/RechartsAreaChart';
import { RechartsPieChart } from '../../components/charts/recharts/RechartsPieChart';

const lineSeries = [
  { name: 'Soja', data: [{ x: 2020, y: 100 }, { x: 2021, y: 120 }] },
  { name: 'Milho', data: [{ x: 2020, y: 80 }, { x: 2021, y: 90 }] },
];

describe('recharts wrappers (agro)', () => {
  it('RechartsLineChart renders an accessible figure with series names', () => {
    render(<RechartsLineChart title="Evolução" series={lineSeries} xlabel="Ano" ylabel="Produção" />);
    const fig = screen.getByRole('img', { name: /evolução/i });
    expect(fig).toBeInTheDocument();
    expect(screen.getAllByText('Soja').length).toBeGreaterThan(0);
  });

  it('RechartsLineChart is keyboard-focusable', () => {
    render(<RechartsLineChart title="Foco" series={lineSeries} />);
    expect(screen.getByRole('img', { name: /foco/i })).toHaveAttribute('tabindex', '0');
  });

  it('RechartsBarChart renders categories', () => {
    render(
      <RechartsBarChart
        title="Área colhida"
        data={[{ category: 'Soja', value: 10 }, { category: 'Milho', value: 5 }]}
      />,
    );
    expect(screen.getByRole('img', { name: /área colhida/i })).toBeInTheDocument();
  });

  it('RechartsAreaChart renders series', () => {
    render(<RechartsAreaChart title="Acumulado" series={lineSeries} />);
    expect(screen.getByRole('img', { name: /acumulado/i })).toBeInTheDocument();
  });

  it('RechartsPieChart renders slices', () => {
    render(
      <RechartsPieChart
        title="Distribuição"
        data={[{ label: 'Soja', value: 60 }, { label: 'Milho', value: 40 }]}
      />,
    );
    expect(screen.getByRole('img', { name: /distribuição/i })).toBeInTheDocument();
    expect(screen.getAllByText('Soja').length).toBeGreaterThan(0);
  });
});
