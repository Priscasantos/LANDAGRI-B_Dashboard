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
