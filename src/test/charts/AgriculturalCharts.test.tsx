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

import AgriculturalCharts from '../../components/overview/AgriculturalCharts';

describe('AgriculturalCharts (recharts)', () => {
  it('renders IBGE/CONAB section heading and does not require plotly', async () => {
    render(<AgriculturalCharts />);
    expect(
      await screen.findByRole('heading', { name: /brazilian agricultural data/i }),
    ).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /production evolution/i })).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /production distribution/i })).toBeInTheDocument();
    expect(await screen.findByRole('img', { name: /area harvested/i })).toBeInTheDocument();
  });

  it('charts are keyboard-focusable', async () => {
    render(<AgriculturalCharts />);
    const chart = await screen.findByRole('img', { name: /production evolution/i });
    chart.focus();
    expect(chart).toHaveFocus();
  });

  it('exposes data source note', async () => {
    render(<AgriculturalCharts />);
    expect(await screen.findByText(/fonte:/i)).toBeInTheDocument();
  });
});
