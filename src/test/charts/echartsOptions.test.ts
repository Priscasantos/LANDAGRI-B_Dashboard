import { describe, expect, it } from 'vitest';
import {
  buildHorizontalBarOption,
  buildGroupedBarOption,
  buildHeatmapOption,
} from '../../components/charts/echarts/echarts-options';
import { CHART_FONT_FAMILY } from '../../lib/fonts';

describe('echarts-options builders (pilot)', () => {
  it('horizontal bar: Berry tooltip, bottom rect legend, divider grid, chart font', () => {
    const option = buildHorizontalBarOption({
      labels: ['SP (Sudeste)', 'BA (Nordeste)'],
      values: [5, 3],
      theme: 'light',
      locale: 'pt-BR',
    });
    const tooltip = option.tooltip as Record<string, unknown>;
    expect(tooltip.backgroundColor).toBe('#1e293b');
    const legend = option.legend as Record<string, unknown>;
    expect(legend.bottom).toBeDefined();
    expect(legend.icon).toBe('rect');
    expect(legend.itemWidth).toBe(8);
    expect(legend.itemHeight).toBe(8);
    const xAxis = option.xAxis as Record<string, unknown>;
    expect(
      (xAxis.splitLine as Record<string, unknown>).lineStyle,
    ).toMatchObject({ color: '#e3e8ef' });
    expect(option.textStyle).toMatchObject({ fontFamily: CHART_FONT_FAMILY });
    expect(typeof tooltip.valueFormatter).toBe('function');
  });

  it('formats numbers per locale (pt-BR decimal comma)', () => {
    const pt = buildHorizontalBarOption({
      labels: ['A'],
      values: [1234.5],
      theme: 'light',
      locale: 'pt-BR',
    });
    const en = buildHorizontalBarOption({
      labels: ['A'],
      values: [1234.5],
      theme: 'light',
      locale: 'en',
    });
    const ptFmt = (pt.tooltip as { valueFormatter: (v: number) => string })
      .valueFormatter;
    const enFmt = (en.tooltip as { valueFormatter: (v: number) => string })
      .valueFormatter;
    expect(ptFmt(1234.5)).toBe((1234.5).toLocaleString('pt-BR'));
    expect(enFmt(1234.5)).toBe((1234.5).toLocaleString('en'));
    expect(ptFmt(1234.5)).not.toBe(enFmt(1234.5));
  });

  it('grouped bar: one series per region with Verde Agro colorway', () => {
    const option = buildGroupedBarOption({
      categories: ['Oct', 'Nov'],
      series: [
        { name: 'Sudeste', values: [4, 5] },
        { name: 'Nordeste', values: [2, 3] },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as unknown[];
    expect(series).toHaveLength(2);
    expect((option.color as string[])?.[0]).toBe('#2E7D32');
    expect((option.legend as Record<string, unknown>).icon).toBe('rect');
  });

  it('heatmap: region x month with visualMap', () => {
    const option = buildHeatmapOption({
      x: ['Oct', 'Nov'],
      y: ['Sudeste', 'Nordeste'],
      z: [
        [4, 5],
        [2, 3],
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    expect(option.visualMap).toBeDefined();
    const series = option.series as unknown[];
    expect(series).toHaveLength(1);
    expect((option.tooltip as Record<string, unknown>).backgroundColor).toBe(
      '#1e293b',
    );
  });

  it('dark theme: Berry tooltip #334155', () => {
    const option = buildHorizontalBarOption({
      labels: ['A'],
      values: [1],
      theme: 'dark',
      locale: 'en',
    });
    expect((option.tooltip as Record<string, unknown>).backgroundColor).toBe(
      '#334155',
    );
    expect((option.color as string[])?.[0]).toBe('#9CCC65');
  });
});
