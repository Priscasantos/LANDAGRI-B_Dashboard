import { describe, expect, it } from 'vitest';
import type { EChartsCoreOption } from 'echarts/core';
import {
  buildGanttOption,
  buildGroupedBarOption,
  buildHeatmapOption,
  buildHorizontalBarOption,
  buildLineOption,
  buildPieOption,
  buildPolarOption,
  buildRadarOption,
  buildScatterOption,
  buildTimelineOption,
} from '../../components/charts/echarts/echarts-options';

interface ToolboxFeature {
  saveAsImage?: { show?: boolean; name?: string; title?: string };
  dataView?: { show?: boolean; title?: string };
}

function toolboxOf(option: EChartsCoreOption): ToolboxFeature {
  const toolbox = option.toolbox as unknown as { feature?: ToolboxFeature } | undefined;
  return toolbox?.feature ?? {};
}

function expectToolbox(
  option: EChartsCoreOption,
  expectedName: string,
): void {
  const feature = toolboxOf(option);
  expect(feature.saveAsImage?.show).toBe(true);
  expect(feature.saveAsImage?.name).toBe(expectedName);
  expect(feature.dataView?.show).toBe(true);
}

describe('echarts toolbox (Expansão #2: download por gráfico)', () => {
  const exportName = 'landagri-temporal-pt-br-evolucao';

  it('horizontal bar: saveAsImage + dataView com títulos PT', () => {
    const option = buildHorizontalBarOption({
      labels: ['A'],
      values: [1],
      theme: 'light',
      locale: 'pt-BR',
      exportName,
    });
    expectToolbox(option, exportName);
    const feature = toolboxOf(option);
    expect(feature.saveAsImage?.title).toBe('Salvar como imagem');
    expect(feature.dataView?.title).toBe('Ver dados');
  });

  it('títulos EN quando locale=en', () => {
    const option = buildHorizontalBarOption({
      labels: ['A'],
      values: [1],
      theme: 'light',
      locale: 'en',
      exportName,
    });
    const feature = toolboxOf(option);
    expect(feature.saveAsImage?.title).toBe('Save as image');
    expect(feature.dataView?.title).toBe('View data');
  });

  it('exportName default inclui locale quando omitido', () => {
    const option = buildPieOption({
      slices: [{ label: 'A', value: 1 }],
      theme: 'dark',
      locale: 'en',
    });
    const feature = toolboxOf(option);
    expect(feature.saveAsImage?.show).toBe(true);
    expect(feature.saveAsImage?.name).toContain('landagri-chart-en');
    expect(feature.dataView?.show).toBe(true);
  });

  it('todos os builders expõem toolbox com o exportName', () => {
    const base = { theme: 'light' as const, locale: 'pt-BR', exportName };
    const options: EChartsCoreOption[] = [
      buildHorizontalBarOption({ ...base, labels: ['A'], values: [1] }),
      buildGroupedBarOption({
        ...base,
        categories: ['A'],
        series: [{ name: 'S', values: [1] }],
      }),
      buildHeatmapOption({ ...base, x: ['A'], y: ['B'], z: [[1]] }),
      buildLineOption({ ...base, series: [{ name: 'S', x: [2020], y: [1] }] }),
      buildPieOption({ ...base, slices: [{ label: 'A', value: 1 }] }),
      buildScatterOption({ ...base, series: [{ name: 'S', data: [[2020, 1]] }] }),
      buildTimelineOption({ ...base, items: [{ label: 'A', years: [2020] }] }),
      buildRadarOption({
        ...base,
        indicators: ['A', 'B'],
        series: [{ name: 'S', values: [1, 2] }],
      }),
      buildGanttOption({
        ...base,
        xLabels: ['Jan', 'Fev'],
        bars: [{ y: 'A', start: 0, duration: 1 }],
      }),
      buildPolarOption({
        ...base,
        categories: ['A', 'B'],
        series: [{ name: 'S', r: [1, 2] }],
      }),
    ];
    expect(options).toHaveLength(10);
    for (const option of options) {
      expectToolbox(option, exportName);
    }
  });
});
