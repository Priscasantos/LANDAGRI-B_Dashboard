import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

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

import ChartContainer from '../../components/charts/ChartContainer';
import { RechartsBarChart } from '../../components/charts/recharts/RechartsBarChart';

describe('ChartContainer (Fase 2: theme-data palette shell)', () => {
  it('renders title + description + children chart', () => {
    render(
      <ChartContainer title="Área colhida" description="Média IBGE/CONAB">
        <RechartsBarChart
          title="Área colhida"
          data={[{ category: 'Soja', value: 10 }]}
        />
      </ChartContainer>,
    );
    expect(screen.getByRole('heading', { name: /área colhida/i })).toBeInTheDocument();
    expect(screen.getByText(/média ibge\/conab/i)).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /área colhida/i })).toBeInTheDocument();
  });

  it('is keyboard-focusable via the inner chart figure', () => {
    render(
      <ChartContainer title="Foco">
        <RechartsBarChart title="Foco" data={[{ category: 'Soja', value: 1 }]} />
      </ChartContainer>,
    );
    const fig = screen.getByRole('img', { name: /foco/i });
    fig.focus();
    expect(fig).toHaveFocus();
  });
});
