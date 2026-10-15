import { describe, expect, it } from 'vitest';
import {
  buildHorizontalBarOption,
  buildGroupedBarOption,
  buildHeatmapOption,
  buildLineOption,
  buildPieOption,
  buildScatterOption,
  buildRadarOption,
  buildGanttOption,
  buildPolarOption,
  buildTimelineOption,
} from '../../components/charts/echarts/echarts-options';
import type { EChartsCoreOption } from 'echarts/core';
import { CHART_FONT_FAMILY } from '../../lib/fonts';
import {
  LANDAGRI_COLORWAY_DARK,
  LANDAGRI_COLORWAY_LIGHT,
  LANDAGRI_DIVERGENT_DARK,
  LANDAGRI_DIVERGENT_LIGHT,
  LANDAGRI_SEQUENTIAL_DARK,
  LANDAGRI_SEQUENTIAL_LIGHT,
  type EChartsPalette,
  type EChartsPilotTheme,
} from '../../lib/echarts-theme';

/** WCAG relative luminance + contrast ratio (test-local, mirrors builder). */
function lum(hex: string): number {
  const n = parseInt(hex.replace('#', ''), 16);
  const lin = (c: number): number => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin((n >> 16) & 255) + 0.7152 * lin((n >> 8) & 255) + 0.0722 * lin(n & 255);
}
function ratio(a: string, b: string): number {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}
function rampAt(ramp: string[], t: number): string {
  const pos = Math.max(0, Math.min(1, t)) * (ramp.length - 1);
  const i = Math.min(Math.floor(pos), ramp.length - 1);
  const j = Math.min(i + 1, ramp.length - 1);
  const f = pos - i;
  const pa = parseInt(ramp[i].replace('#', ''), 16);
  const pb = parseInt(ramp[j].replace('#', ''), 16);
  const mix = (shift: number): number =>
    Math.round(((pa >> shift) & 255) + ((((pb >> shift) & 255) - ((pa >> shift) & 255)) * f));
  return `#${((mix(16) << 16) | (mix(8) << 8) | mix(0)).toString(16).padStart(6, '0')}`;
}

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

  it('line: one series per name, category years, Verde Agro colorway', () => {
    const option = buildLineOption({
      series: [
        { name: 'Soja', x: [2020, 2021], y: [100, 120] },
        { name: 'Milho', x: [2020, 2021], y: [80, 90], color: '#EC9706' },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as Record<string, unknown>[];
    expect(series).toHaveLength(2);
    expect(series[0]).toMatchObject({ type: 'line', name: 'Soja' });
    expect((option.xAxis as Record<string, unknown>).data).toEqual([
      2020, 2021,
    ]);
    expect((option.color as string[])?.[0]).toBe('#2E7D32');
    expect((series[1].lineStyle as Record<string, unknown>).color).toBe(
      '#EC9706',
    );
    expect((option.tooltip as Record<string, unknown>).trigger).toBe('axis');
    expect(option.textStyle).toMatchObject({ fontFamily: CHART_FONT_FAMILY });
  });

  it('line: areaFill + hidden markers mirror Plotly fill/showMarkers', () => {
    const option = buildLineOption({
      series: [{ name: 'A', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
      showMarkers: false,
      areaFill: true,
    });
    const s = (option.series as Record<string, unknown>[])[0];
    expect(s).toMatchObject({ symbol: 'none' });
    expect(s.areaStyle).toBeDefined();
  });

  it('pie: slices with percent labels, donut radius when donut', () => {
    const option = buildPieOption({
      slices: [
        { label: 'Soja', value: 60 },
        { label: 'Milho', value: 40 },
      ],
      theme: 'light',
      locale: 'pt-BR',
      donut: true,
    });
    const s = (option.series as Record<string, unknown>[])[0];
    expect(s).toMatchObject({ type: 'pie', radius: ['40%', '68%'] });
    expect(s.data).toHaveLength(2);
    expect(
      ((s.data as Record<string, unknown>[])[0].itemStyle as Record<string, unknown>).color,
    ).toBe('#2E7D32');
    expect((option.tooltip as Record<string, unknown>).backgroundColor).toBe(
      '#1e293b',
    );
  });

  it('scatter: value axes with locale formatters', () => {
    const option = buildScatterOption({
      series: [{ name: 'A', data: [[2020, 100], [2021, 120]] }],
      theme: 'dark',
      locale: 'en',
    });
    const s = (option.series as Record<string, unknown>[])[0];
    expect(s).toMatchObject({ type: 'scatter', symbolSize: 8 });
    expect((option.xAxis as Record<string, unknown>).type).toBe('value');
    expect((option.color as string[])?.[0]).toBe('#9CCC65');
  });

  it('radar: indicators with per-axis max, area fill', () => {
    const option = buildRadarOption({
      indicators: ['Produtividade', 'Área'],
      series: [{ name: 'Soja', values: [80, 60] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const s = (option.series as Record<string, unknown>[])[0];
    expect(s).toMatchObject({ type: 'radar' });
    expect(option.radar).toMatchObject({
      indicator: [
        { name: 'Produtividade', max: 80 },
        { name: 'Área', max: 60 },
      ],
    });
    expect(
      ((s.data as Record<string, unknown>[])[0].areaStyle as Record<string, unknown>).opacity,
    ).toBe(0.12);
  });

  it('builders inherit the active font when fontFamily is passed', () => {
    const mono = '"JetBrains Mono", monospace';
    const option = buildLineOption({
      series: [{ name: 'A', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
      fontFamily: mono,
    });
    expect(option.textStyle).toMatchObject({ fontFamily: mono });
    expect(
      (
        (option.tooltip as Record<string, unknown>).textStyle as Record<string, unknown>
      ).fontFamily,
    ).toBe(mono);
  });
});

describe('echarts-options builders (fatia 2b — CropCalendar)', () => {
  it('heatmap honors custom colors + min/max (calendar spikes)', () => {
    const option = buildHeatmapOption({
      x: ['Oct', 'Nov'],
      y: ['Soja'],
      z: [[1, 3]],
      theme: 'light',
      locale: 'pt-BR',
      colors: ['#f3f4f6', '#22c55e', '#f97316', '#3b82f6'],
      min: 0,
      max: 3,
    });
    expect(option.visualMap).toMatchObject({
      min: 0,
      max: 3,
      inRange: { color: ['#f3f4f6', '#22c55e', '#f97316', '#3b82f6'] },
    });
  });

  it('gantt: ghost base + duration stack, first bar on top, month labels', () => {
    const months = ['Oct', 'Nov', 'Dec'];
    const option = buildGanttOption({
      xLabels: months,
      bars: [
        { y: 'Soja P (MT)', start: 0, duration: 2.5, tip: 'Soja' },
        { y: 'Milho H (PR)', start: 1, duration: 1.5, tip: 'Milho' },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as Record<string, unknown>[];
    expect(series).toHaveLength(2);
    expect(series[0]).toMatchObject({ type: 'bar', stack: 'gantt' });
    expect(series[1]).toMatchObject({ type: 'bar', stack: 'gantt' });
    // Ghost base is silent/transparent
    expect(series[0]).toMatchObject({
      silent: true,
      itemStyle: { color: 'transparent' },
    });
    // First bar renders on top (inverse category axis)
    expect(option.yAxis).toMatchObject({ inverse: true });
    // Value axis spans the month index range with month labels
    expect(option.xAxis).toMatchObject({ type: 'value', min: -0.5, max: 2.5 });
    const xAxis = option.xAxis as {
      axisLabel: { formatter: (v: number) => string };
    };
    expect(xAxis.axisLabel.formatter(1)).toBe('Nov');
    expect((option.tooltip as Record<string, unknown>).backgroundColor).toBe(
      '#1e293b',
    );
  });

  it('polar: line on polar coords with month angle axis', () => {
    const option = buildPolarOption({
      categories: ['Oct', 'Nov', 'Dec'],
      series: [{ name: 'Total Activity', r: [3, 5, 2] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as Record<string, unknown>[];
    expect(series).toHaveLength(1);
    expect(series[0]).toMatchObject({
      type: 'line',
      coordinateSystem: 'polar',
    });
    expect(option.angleAxis).toMatchObject({
      type: 'category',
      data: ['Oct', 'Nov', 'Dec'],
    });
    expect(option.polar).toBeDefined();
    expect((option.tooltip as Record<string, unknown>).backgroundColor).toBe(
      '#1e293b',
    );
  });
});

describe('echarts-options builders (fatia 2c)', () => {
  it('line: dashed average series renders dashed lineStyle', () => {
    const option = buildLineOption({
      series: [
        { name: 'Ativas', x: [2020, 2021], y: [3, 5] },
        { name: 'Média (4)', x: [2020, 2021], y: [4, 4], dash: 'dash' },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as { lineStyle: Record<string, unknown> }[];
    expect(series).toHaveLength(2);
    expect(series[1].lineStyle.type).toBe('dashed');
    expect(series[0].lineStyle.type ?? 'solid').toBe('solid');
  });

  it('line: stacked series share a stack with fill', () => {
    const option = buildLineOption({
      series: [
        { name: 'Alta', x: [2020], y: [1] },
        { name: 'Média', x: [2020], y: [2] },
      ],
      theme: 'light',
      locale: 'pt-BR',
      stack: true,
    });
    const series = option.series as Record<string, unknown>[];
    expect(series[0].stack).toBe('total');
    expect(series[1].stack).toBe('total');
    expect(series[0].areaStyle).toBeDefined();
  });

  it('grouped bar: referenceLine renders a dashed markLine', () => {
    const option = buildGroupedBarOption({
      categories: ['A', 'B'],
      series: [{ name: 'Gap', values: [0, 3] }],
      referenceLine: { value: 1.5, name: 'Média (1.5)' },
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      markLine: { data: { yAxis: number; name: string }[] };
    }[];
    expect(series[0].markLine.data[0].yAxis).toBe(1.5);
    expect(series[0].markLine.data[0].name).toBe('Média (1.5)');
  });

  it('grouped bar: stacked renders a shared stack', () => {
    const option = buildGroupedBarOption({
      categories: ['A'],
      series: [
        { name: 'Agri', values: [60] },
        { name: 'Outras', values: [40] },
      ],
      stacked: true,
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as Record<string, unknown>[];
    expect(series[0].stack).toBe('total');
    expect(series[1].stack).toBe('total');
  });

  it('scatter: log y axis with bubble sizes and top labels', () => {
    const option = buildScatterOption({
      series: [
        {
          name: 'MapBiomas',
          data: [
            [85.5, 30],
            [90.1, 10],
          ],
          sizes: [12, 37],
          labels: ['MapBiomas', 'Outra'],
        },
      ],
      yAxisType: 'log',
      theme: 'light',
      locale: 'pt-BR',
    });
    expect(option.yAxis).toMatchObject({ type: 'log' });
    const series = option.series as {
      symbolSize: unknown;
      label: Record<string, unknown>;
    }[];
    expect(typeof series[0].symbolSize).toBe('function');
    expect(series[0].label).toMatchObject({ show: true, position: 'top' });
  });

  it('timeline: one line + one scatter series per initiative, reversed categories', () => {
    const option = buildTimelineOption({
      items: [
        { label: 'MapBiomas', years: [2000, 2001, 2003], color: '#2E7D32' },
        { label: 'TerraClass', years: [2004, 2008], color: '#43A047' },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as { type: string }[];
    expect(series).toHaveLength(4);
    expect(series.map((s) => s.type)).toEqual([
      'line',
      'scatter',
      'line',
      'scatter',
    ]);
    expect(option.yAxis).toMatchObject({ type: 'category', inverse: true });
  });

  it('line: markPoint pins the peak year', () => {
    const option = buildLineOption({
      series: [
        {
          name: 'Ativas',
          x: [2020, 2021],
          y: [3, 5],
          markPoint: { x: 2021, label: 'Pico: 2021' },
        },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      markPoint: { data: { coord: [number, number]; name: string }[] };
    }[];
    expect(series[0].markPoint.data[0].coord).toEqual([2021, 5]);
    expect(series[0].markPoint.data[0].name).toBe('Pico: 2021');
  });

  it('grouped bar: log y axis for resolution meters', () => {
    const option = buildGroupedBarOption({
      categories: ['A', 'B'],
      series: [{ name: 'Resolução', values: [10, 1000] }],
      yAxisType: 'log',
      theme: 'light',
      locale: 'pt-BR',
    });
    expect(option.yAxis).toMatchObject({ type: 'log' });
  });

  it('heatmap: showValues renders cell labels', () => {
    const option = buildHeatmapOption({
      x: ['A', 'B'],
      y: ['A', 'B'],
      z: [
        [1, 0.5],
        [0.5, 1],
      ],
      theme: 'light',
      locale: 'pt-BR',
      showValues: true,
    });
    const series = option.series as {
      label: Record<string, unknown>;
    }[];
    expect(series[0].label).toMatchObject({ show: true });
  });

  it('grouped bar: per-series color override', () => {
    const option = buildGroupedBarOption({
      categories: ['A'],
      series: [
        { name: 'Total', values: [10], color: '#3b82f6' },
        { name: 'Agri', values: [6], color: '#22c55e' },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      itemStyle: { color: string };
    }[];
    expect(series[0].itemStyle.color).toBe('#3b82f6');
    expect(series[1].itemStyle.color).toBe('#22c55e');
  });
});

describe('echarts-options typographic pass (reversible)', () => {
  const ax = (o: object, key: 'xAxis' | 'yAxis'): Record<string, unknown> =>
    (o as Record<string, Record<string, unknown>>)[key] as Record<string, unknown>;
  const axisLabel = (o: object, key: 'xAxis' | 'yAxis'): Record<string, unknown> =>
    ax(o, key).axisLabel as Record<string, unknown>;

  it('axis tick labels meet AA contrast per theme (light #64748b, dark #94a3b8)', () => {
    const light = buildLineOption({
      series: [{ name: 'A', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const dark = buildLineOption({
      series: [{ name: 'A', x: [2020], y: [1] }],
      theme: 'dark',
      locale: 'pt-BR',
    });
    expect(axisLabel(light, 'xAxis').color).toBe('#64748b');
    expect(axisLabel(light, 'yAxis').color).toBe('#64748b');
    expect(axisLabel(dark, 'xAxis').color).toBe('#94a3b8');
    expect(axisLabel(dark, 'yAxis').color).toBe('#94a3b8');
  });

  it('axis ticks use Inter 12px with fontFamily + hideOverlap on categories', () => {
    const option = buildLineOption({
      series: [{ name: 'A', x: [2020, 2021], y: [1, 2] }],
      theme: 'light',
      locale: 'pt-BR',
      fontFamily: 'Inter, sans-serif',
    });
    const label = axisLabel(option, 'xAxis');
    expect(label.fontSize).toBe(12);
    expect(label.fontFamily).toBe('Inter, sans-serif');
    expect(label.hideOverlap).toBe(true);
    expect(axisLabel(option, 'yAxis').fontSize).toBe(12);
  });

  it('legend wraps bottom in Inter 12px with spacing', () => {
    const option = buildGroupedBarOption({
      categories: ['A'],
      series: [{ name: 'S', values: [1] }],
      theme: 'light',
      locale: 'pt-BR',
      fontFamily: 'Inter, sans-serif',
    });
    const legend = option.legend as Record<string, unknown>;
    const textStyle = legend.textStyle as Record<string, unknown>;
    expect(textStyle.fontSize).toBe(12);
    expect(textStyle.fontFamily).toBe('Inter, sans-serif');
    expect(legend.bottom).toBe(0);
  });

  it('legend-heavy charts reserve grid bottom so wrapped rows never hit the axis', () => {
    const many = Array.from({ length: 12 }, (_, i) => ({
      name: `Initiative number ${i} with a long name`,
      x: [2020],
      y: [i],
    }));
    const crowded = buildLineOption({
      series: many,
      theme: 'light',
      locale: 'pt-BR',
    });
    const roomy = buildLineOption({
      series: [{ name: 'A', x: [2020], y: [1] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const gridCrowded = crowded.grid as Record<string, unknown>;
    const gridRoomy = roomy.grid as Record<string, unknown>;
    expect(gridCrowded.bottom as number).toBeGreaterThan(
      gridRoomy.bottom as number,
    );
    expect(gridCrowded.bottom as number).toBeGreaterThanOrEqual(80);
  });

  it('grouped bar truncates very long category labels (full name stays in tooltip)', () => {
    const long =
      'PRODES Deforestation, Warnings and Vegetation for Brazilian Biomes (PRODES)';
    const option = buildGroupedBarOption({
      categories: [long, 2020],
      series: [{ name: 'S', values: [1, 2] }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const label = axisLabel(option, 'xAxis');
    const fmt = label.formatter as (v: unknown) => string;
    const truncated = fmt(long);
    expect(truncated.length).toBeLessThan(long.length);
    expect(truncated).toMatch(/…$/);
    expect(fmt(2020)).toBe('2020');
  });

  it('heatmap thins crowded year axes but keeps short month axes intact', () => {
    const years = Array.from({ length: 40 }, (_, i) => 1985 + i);
    const crowded = buildHeatmapOption({
      x: years,
      y: ['A'],
      z: [years.map(() => 1)],
      theme: 'light',
      locale: 'pt-BR',
    });
    const months2 = buildHeatmapOption({
      x: ['Oct', 'Nov', 'Dec'],
      y: ['A'],
      z: [[1, 2, 3]],
      theme: 'light',
      locale: 'pt-BR',
    });
    const crowdedLabel = axisLabel(crowded, 'xAxis');
    const monthsLabel = axisLabel(months2, 'xAxis');
    expect(crowdedLabel.interval as number).toBeGreaterThan(0);
    expect(monthsLabel.interval as number).toBe(0);
  });

  it('heatmap reserves room for rotated labels + visualMap (no collision)', () => {
    const option = buildHeatmapOption({
      x: ['Oct'],
      y: ['A'],
      z: [[1]],
      theme: 'light',
      locale: 'pt-BR',
    });
    const grid = option.grid as Record<string, unknown>;
    const visualMap = option.visualMap as Record<string, unknown>;
    expect(grid.bottom as number).toBeGreaterThanOrEqual(96);
    expect(visualMap.bottom as number).toBeLessThanOrEqual(12);
  });

  it('pie hides overlapping slice labels instead of stacking them', () => {
    const option = buildPieOption({
      slices: [
        { label: 'Big', value: 80 },
        { label: 'Tiny a', value: 0.1 },
        { label: 'Tiny b', value: 0.1 },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as { labelLayout?: Record<string, unknown> }[];
    expect(series[0].labelLayout).toMatchObject({ hideOverlap: true });
  });

  it('scatter hides overlapping point labels and reserves legend room', () => {
    const option = buildScatterOption({
      series: Array.from({ length: 12 }, (_, i) => ({
        name: `Initiative ${i} with a long name`,
        data: [[80 + i, 90]] as [number, number | null][],
        labels: [`Initiative ${i} with a long name`],
      })),
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      label?: Record<string, unknown>;
      labelLayout?: Record<string, unknown>;
    }[];
    expect(series[0].labelLayout).toMatchObject({ hideOverlap: true });
    const grid = option.grid as Record<string, unknown>;
    expect(grid.bottom as number).toBeGreaterThanOrEqual(80);
  });

  it('gantt x formatter never renders out-of-range duplicates', () => {
    const option = buildGanttOption({
      xLabels: ['Oct', 'Nov'],
      bars: [{ y: 'A', start: 0, duration: 1 }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const fmt = axisLabel(option, 'xAxis').formatter as (v: number) => string;
    expect(fmt(-0.5)).toBe('');
    expect(fmt(99)).toBe('');
    expect(fmt(0.2)).toBe('');
    expect(fmt(0)).toBe('Oct');
    expect(fmt(1)).toBe('Nov');
  });

  it('timeline year axis stays integer with decade-snapped bounds', () => {
    const option = buildTimelineOption({
      items: [
        { label: 'A', years: [2001, 2023] },
        { label: 'B', years: [1985, 2000] },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const x = ax(option, 'xAxis');
    const fmt = axisLabel(option, 'xAxis').formatter as (v: number) => string;
    expect(fmt(2000.5)).toBe('2001');
    expect(fmt(2020)).toBe('2020');
    expect(x.minInterval).toBe(1);
    expect((x.min as number) % 5).toBe(0);
    expect((x.max as number) % 5).toBe(0);
    expect(x.min as number).toBeLessThanOrEqual(1985);
    expect(x.max as number).toBeGreaterThanOrEqual(2023);
  });

  it('heatmap cell values stay legible on light cells (adaptive label color)', () => {
    const option = buildHeatmapOption({
      x: ['A', 'B'],
      y: ['R'],
      z: [[0, 1]],
      min: -1,
      max: 1,
      showValues: true,
      labelDarkRange: [-0.35, 0.35],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      label?: { color?: unknown };
    }[];
    const color = series[0].label?.color;
    expect(typeof color).toBe('function');
    const fn = color as (p: { value?: unknown }) => string;
    expect(fn({ value: [0, 0, 0] })).toBe('#1e293b');
    expect(fn({ value: [0, 0, 1] })).toBe('#ffffff');
    expect(fn({ value: [0, 0, -1] })).toBe('#ffffff');
  });
});

describe('echarts-options pie tiny-slice labels', () => {
  it('hides outer labels for slices under 1% (legend + tooltip keep the data)', async () => {
    const { buildPieOption } = await import(
      '../../components/charts/echarts/echarts-options'
    );
    const option = buildPieOption({
      slices: [
        { label: 'Big', value: 98 },
        { label: 'Sliver', value: 0.5 },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const s = (option.series as Record<string, unknown>[])[0];
    const fmt = (s.label as { formatter: (p: object) => string }).formatter;
    expect(fmt({ name: 'Big', percent: 98 })).toContain('Big');
    expect(fmt({ name: 'Sliver', percent: 0.5 })).toBe('');
  });
});

describe('echarts-options scatter cross-series declutter', () => {
  it('keeps isolated point labels, hides colliding cluster labels (tooltip keeps all)', async () => {
    const { buildScatterOption } = await import(
      '../../components/charts/echarts/echarts-options'
    );
    const cluster = Array.from({ length: 8 }, (_, i) => ({
      name: `Cluster initiative ${i} with a very long name`,
      data: [[90 + i * 0.2, 20 + (i % 3)]] as [number, number | null][],
      labels: [`Cluster initiative ${i} with a very long name`],
    }));
    const option = buildScatterOption({
      series: [
        ...cluster,
        {
          name: 'Far away outlier with a long name',
          data: [[10, 90]],
          labels: ['Far away outlier with a long name'],
        },
      ],
      theme: 'light',
      locale: 'pt-BR',
    });
    const series = option.series as {
      label?: Record<string, unknown>;
      data: { value: [number, number]; label?: { show: boolean } }[];
    }[];
    // Outlier isolado mantém o rótulo.
    const outlier = series[series.length - 1];
    const outlierShown =
      (outlier.label as { show?: boolean } | undefined)?.show !== false &&
      outlier.data.every((d) => d.label?.show !== false);
    expect(outlierShown).toBe(true);
    // No aglomerado, a maioria perde o rótulo (sem blob ilegível).
    const clusterHidden = cluster
      .map((_, i) => series[i])
      .filter(
        (s) =>
          (s.label as { show?: boolean } | undefined)?.show === false ||
          s.data.some((d) => d.label?.show === false),
      ).length;
    expect(clusterHidden).toBeGreaterThan(0);
  });
});

describe('echarts-options palette (theme | divergent)', () => {
  const heatBase: {
    x: (string | number)[];
    y: (string | number)[];
    z: (number | null)[][];
    locale: string;
  } = {
    x: ['A', 'B'],
    y: ['R'],
    z: [[0, 1]],
    locale: 'pt-BR',
  };

  function visualColors(option: EChartsCoreOption): string[] {
    const vm = option.visualMap as unknown as { inRange: { color: string[] } };
    return vm.inRange.color;
  }

  function cellLabelFn(option: EChartsCoreOption): (p: { value?: unknown }) => string {
    const series = option.series as { label: { color: unknown } }[];
    return series[0].label.color as (p: { value?: unknown }) => string;
  }

  it('heatmap default palette is theme sequential (light/dark differ)', () => {
    const light = buildHeatmapOption({ ...heatBase, theme: 'light' });
    const dark = buildHeatmapOption({ ...heatBase, theme: 'dark' });
    expect(visualColors(light)).toEqual([...LANDAGRI_SEQUENTIAL_LIGHT]);
    expect(visualColors(dark)).toEqual([...LANDAGRI_SEQUENTIAL_DARK]);
    expect(visualColors(light)).not.toEqual(visualColors(dark));
  });

  it("heatmap palette 'divergent' resolves the documented green↔earth/red scale", () => {
    const light = buildHeatmapOption({ ...heatBase, theme: 'light', palette: 'divergent' });
    const dark = buildHeatmapOption({ ...heatBase, theme: 'dark', palette: 'divergent' });
    expect(visualColors(light)).toEqual([...LANDAGRI_DIVERGENT_LIGHT]);
    expect(visualColors(dark)).toEqual([...LANDAGRI_DIVERGENT_DARK]);
    // Divergent differs from the sequential theme ramp in both themes.
    expect(visualColors(light)).not.toEqual([...LANDAGRI_SEQUENTIAL_LIGHT]);
    expect(visualColors(dark)).not.toEqual([...LANDAGRI_SEQUENTIAL_DARK]);
  });

  it('explicit heatmap colors override any palette (reversible escape hatch)', () => {
    const custom = ['#f3f4f6', '#22c55e', '#f97316', '#3b82f6'];
    const option = buildHeatmapOption({
      ...heatBase,
      theme: 'light',
      palette: 'divergent',
      colors: custom,
      min: 0,
      max: 3,
    });
    expect(visualColors(option)).toEqual(custom);
  });

  it('categorical builders stay on the theme colorway even with divergent (ignored by design)', () => {
    const bars = buildGroupedBarOption({
      categories: ['A'],
      series: [{ name: 'S', values: [1] }],
      theme: 'light',
      locale: 'pt-BR',
      palette: 'divergent',
    });
    expect(bars.color).toEqual([...LANDAGRI_COLORWAY_LIGHT]);
    const darkLine = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1] }],
      theme: 'dark',
      locale: 'pt-BR',
      palette: 'divergent',
    });
    expect(darkLine.color).toEqual([...LANDAGRI_COLORWAY_DARK]);
  });

  it('heatmap cell labels pick max-contrast text automatically (AA, both themes)', () => {
    const light = buildHeatmapOption({ ...heatBase, theme: 'light', min: 0, max: 1, showValues: true });
    const dark = buildHeatmapOption({ ...heatBase, theme: 'dark', min: 0, max: 1, showValues: true });
    // Light sequential: pale bottom → dark Berry text; saturated top → white.
    expect(cellLabelFn(light)({ value: [0, 0, 0] })).toBe('#1e293b');
    expect(cellLabelFn(light)({ value: [0, 0, 1] })).toBe('#ffffff');
    // Dark sequential: dark slate bottom → white; bright green top → dark text.
    expect(cellLabelFn(dark)({ value: [0, 0, 0] })).toBe('#ffffff');
    expect(cellLabelFn(dark)({ value: [0, 0, 1] })).toBe('#1e293b');
    // Divergent correlation: saturated endpoints → white in both themes.
    const divLight = buildHeatmapOption({
      ...heatBase,
      z: [[-1, 1]],
      theme: 'light',
      palette: 'divergent',
      min: -1,
      max: 1,
      showValues: true,
    });
    expect(cellLabelFn(divLight)({ value: [0, 0, -1] })).toBe('#ffffff');
    expect(cellLabelFn(divLight)({ value: [0, 0, 1] })).toBe('#ffffff');
  });

  it('heatmap ramps keep >=4.5:1 label contrast at sampled stops (AA, both themes/palettes)', () => {
    const combos: [EChartsPalette, EChartsPilotTheme][] = [
      ['theme', 'light'],
      ['theme', 'dark'],
      ['divergent', 'light'],
      ['divergent', 'dark'],
    ];
    for (const [palette, theme] of combos) {
      const option = buildHeatmapOption({
        ...heatBase,
        theme,
        palette,
        min: 0,
        max: 1,
        showValues: true,
      });
      const ramp = visualColors(option);
      const labelCfg = (option.series as { label: { textBorderWidth: number; textBorderColor: string } }[])[0].label;
      expect(labelCfg.textBorderWidth).toBe(2);
      expect(labelCfg.textBorderColor).toBe(
        theme === 'dark' ? 'rgba(255,255,255,0.85)' : 'rgba(30,41,59,0.85)',
      );
      for (const t of [0, 0.25, 0.5, 0.75, 1]) {
        const label = cellLabelFn(option)({ value: [0, 0, t] });
        expect(
          ratio(rampAt(ramp, t), label),
          `${palette}/${theme} @${t}`,
        ).toBeGreaterThanOrEqual(4.5);
      }
    }
  });

  it('reference line defaults to the theme neutral; markPoint to theme amber', () => {
    const bars = buildGroupedBarOption({
      categories: ['A'],
      series: [{ name: 'S', values: [1] }],
      referenceLine: { value: 1, name: 'avg' },
      theme: 'light',
      locale: 'pt-BR',
    });
    const first = (bars.series as { markLine: { lineStyle: { color: string } } }[])[0];
    expect(first.markLine.lineStyle.color).toBe('#64748b');
    const darkBars = buildGroupedBarOption({
      categories: ['A'],
      series: [{ name: 'S', values: [1] }],
      referenceLine: { value: 1, name: 'avg' },
      theme: 'dark',
      locale: 'pt-BR',
    });
    const darkFirst = (darkBars.series as { markLine: { lineStyle: { color: string } } }[])[0];
    expect(darkFirst.markLine.lineStyle.color).toBe('#94a3b8');

    const line = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1], markPoint: { x: 2020, label: 'peak' } }],
      theme: 'light',
      locale: 'pt-BR',
    });
    const ls = line.series as { markPoint: { itemStyle: { color: string } } }[];
    expect(ls[0].markPoint.itemStyle.color).toBe(LANDAGRI_COLORWAY_LIGHT[6]);
    const darkLine = buildLineOption({
      series: [{ name: 'S', x: [2020], y: [1], markPoint: { x: 2020, label: 'peak' } }],
      theme: 'dark',
      locale: 'pt-BR',
    });
    const dls = darkLine.series as { markPoint: { itemStyle: { color: string } } }[];
    expect(dls[0].markPoint.itemStyle.color).toBe(LANDAGRI_COLORWAY_DARK[6]);
  });
});
