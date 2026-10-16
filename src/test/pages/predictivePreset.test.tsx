import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';

vi.mock('recharts', async (importOriginal) => {
  const actual = await importOriginal<typeof import('recharts')>();
  const React = await import('react');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children: React.ReactElement }) =>
      React.cloneElement(
        children as React.ReactElement<{ width?: number; height?: number }>,
        { width: 600, height: 320 },
      ),
  };
});

vi.mock('../../components/charts/echarts/EChartsBase', () => ({
  default: ({ option, ariaLabel }: { option: { color?: string[] }; ariaLabel: string }) => (
    <div
      data-testid="echarts-probe"
      data-colors={JSON.stringify(option.color ?? [])}
      aria-label={ariaLabel}
    />
  ),
}));

import PredictivePage from '../../pages/PredictivePage';
import { ThemeProvider } from '../../components/theme-provider';

const AGRO_GREEN = '#2e7d32';
const AZUL_FIRST_LIGHT = '#2563eb';
const TERRA_FIRST_LIGHT = '#80400B';
const AZUL_FIRST_DARK = '#93c5fd';

function renderPage(theme: 'light' | 'dark' = 'light') {
  return render(
    <MemoryRouter>
      <ThemeProvider defaultTheme={theme}>
        <PredictivePage />
      </ThemeProvider>
    </MemoryRouter>,
  );
}

/** Valores de `stroke` das curvas do recharts (séries — sem o grid). */
function rechartsStrokes(container: HTMLElement): string[] {
  return Array.from(container.querySelectorAll('.recharts-line [stroke]'))
    .map((el) => el.getAttribute('stroke') ?? '')
    .filter((v) => v !== '' && v !== 'none');
}

function echartsColors(): string[] {
  const probe = screen.getByTestId('echarts-probe');
  return JSON.parse(probe.getAttribute('data-colors') ?? '[]') as string[];
}

beforeEach(() => {
  delete document.documentElement.dataset.preset;
});

afterEach(() => {
  delete document.documentElement.dataset.preset;
});

describe('PredictivePage segue o preset ativo (Azul↔Verde↔Terra)', () => {
  it('com preset Azul, charts usam o colorway azul — sem verde Agro travado', () => {
    document.documentElement.dataset.preset = 'default';
    const { container } = renderPage('light');

    const strokes = rechartsStrokes(container);
    expect(strokes.length).toBeGreaterThan(0);
    expect(strokes).toContain(AZUL_FIRST_LIGHT);
    for (const s of strokes) {
      expect(s.startsWith('var(')).toBe(false);
      expect(s.toLowerCase()).not.toBe(AGRO_GREEN);
    }

    expect(echartsColors()[0]).toBe(AZUL_FIRST_LIGHT);
  });

  it('trocar Azul→Terra em runtime reconstrói as cores (recharts + ECharts)', async () => {
    document.documentElement.dataset.preset = 'default';
    const { container } = renderPage('light');
    expect(echartsColors()[0]).toBe(AZUL_FIRST_LIGHT);

    document.documentElement.dataset.preset = 'terra';

    await waitFor(() => {
      expect(echartsColors()[0]).toBe(TERRA_FIRST_LIGHT);
    });
    const strokes = rechartsStrokes(container);
    expect(strokes).toContain(TERRA_FIRST_LIGHT);
    for (const s of strokes) {
      expect(s.startsWith('var(')).toBe(false);
    }
  });

  it('com preset Azul no dark, charts usam o colorway azul escuro', () => {
    document.documentElement.dataset.preset = 'default';
    const { container } = renderPage('dark');

    const strokes = rechartsStrokes(container);
    expect(strokes.length).toBeGreaterThan(0);
    expect(strokes).toContain(AZUL_FIRST_DARK);
    expect(echartsColors()[0]).toBe(AZUL_FIRST_DARK);
  });
});
