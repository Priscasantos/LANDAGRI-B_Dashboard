import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import * as React from 'react';
import {
  buildGroupedBarOption,
  buildHeatmapOption,
  buildHorizontalBarOption,
  buildLineOption,
  buildPieOption,
} from '../../components/charts/echarts/echarts-options';
import {
  LANDAGRI_DIVERGENT_LIGHT,
  LANDAGRI_SEQUENTIAL_LIGHT,
  heatmapVisualColors,
} from '../../lib/echarts-theme';
import {
  DIVERGENT_NEGATIVE,
  divergentRampForPreset,
  divergingColorForValue,
  mixHex,
  presetCharts,
  presetNegative,
  presetPrimary,
  sequentialRampForPreset,
  sidebarDivergentVars,
} from '../../lib/chart-preset';
import { getChartLayout } from '../../lib/chartDefaults';
import { getThemePreset } from '../../config/theme-presets';
import { readChartColorway, useChartColorway } from '../../hooks/use-chart-colorway';
import { useThemeManager } from '../../hooks/use-theme-manager';
import { ThemeProvider } from '../../components/theme-provider';

function installMemoryStorage(): void {
  const store = new Map<string, string>();
  vi.stubGlobal('localStorage', {
    getItem: (k: string) => (store.has(k) ? store.get(k) : null),
    setItem: (k: string, v: string) => void store.set(k, String(v)),
    removeItem: (k: string) => void store.delete(k),
    clear: () => void store.clear(),
  } as Storage);
}

function themeWrapper({ children }: { children: React.ReactNode }) {
  return React.createElement(ThemeProvider, null, children);
}

beforeEach(() => {
  installMemoryStorage();
  delete document.documentElement.dataset.preset;
  delete document.documentElement.dataset.palette;
});

afterEach(() => {
  vi.unstubAllGlobals();
  delete document.documentElement.dataset.preset;
  delete document.documentElement.dataset.palette;
});

describe('chart-preset (cores derivadas do preset ativo)', () => {
  it('resolve a colorway categórica por preset + tema', () => {
    expect(presetCharts('terra', 'light')[0]).toBe('#80400B');
    expect(presetCharts('agro-v2', 'dark')[0]).toBe('#9CCC65');
    expect(presetCharts('ambar', 'light')[0]).toBe('#EC9706');
    expect(presetCharts('terra', 'light')).toHaveLength(10);
    // Preset desconhecido → fallback agro-v2 (default do app).
    expect(presetCharts('inexistente', 'light')[0]).toBe(
      getThemePreset('agro-v2').light.charts[0],
    );
  });

  it('mistura hex nos extremos e no ponto médio', () => {
    expect(mixHex('#000000', '#ffffff', 0)).toBe('#000000');
    expect(mixHex('#000000', '#ffffff', 1)).toBe('#ffffff');
    expect(mixHex('#000000', '#ffffff', 0.5)).toBe('#808080');
    expect(mixHex('invalida', '#ffffff', 0.5)).toBe('#000000');
  });

  it('rampa sequencial vai do neutro à primária do preset', () => {
    const terra = sequentialRampForPreset('terra', 'light');
    expect(terra).toHaveLength(5);
    expect(terra[0]).toBe('#f1f5f1');
    expect(terra[3]).toBe('#80400B');
    const agro = sequentialRampForPreset('agro-v2', 'light');
    expect(agro[3]).toBe('#2E7D32');
    expect(terra).not.toEqual(agro);
    const dark = sequentialRampForPreset('terra', 'dark');
    expect(dark[0]).toBe('#233042');
    expect(dark[3]).toBe('#d08a3e');
  });

  it('rampa divergente ancora o negativo por preset e o positivo na primária', () => {
    const terra = divergentRampForPreset('terra', 'light');
    expect(terra).toHaveLength(5);
    expect(terra[0]).toBe(DIVERGENT_NEGATIVE.terra.light);
    expect(terra[4]).toBe(presetPrimary('terra', 'light'));
    const agro = divergentRampForPreset('agro-v2', 'light');
    expect(agro[0]).toBe('#b2182b');
    expect(agro[4]).toBe('#2E7D32');
    expect(terra[0]).not.toBe(agro[0]);
  });

  it('cor divergente por valor codifica o sinal em torno de 0', () => {
    expect(divergingColorForValue(-3, 'terra', 'light')).toBe(
      presetNegative('terra', 'light'),
    );
    expect(divergingColorForValue(5, 'terra', 'light')).toBe('#80400B');
    expect(divergingColorForValue(0, 'terra', 'light')).toBe('#80400B');
    expect(divergingColorForValue(null, 'terra', 'light')).toBe('#B0BEC5');
  });

  it('sidebar divergente densifica o preset sem trocar o matiz', () => {
    for (const value of ['default', 'agro', 'agro-v2', 'terra', 'ambar'] as const) {
      for (const theme of ['light', 'dark'] as const) {
        const base = getThemePreset(value)[theme];
        const hc = sidebarDivergentVars(value, theme);
        expect(hc.sidebarActiveBg).not.toBe(base.sidebarActiveBg);
        expect(hc.sidebarTextActive).not.toBe(base.sidebarTextActive);
      }
    }
  });
});

describe('heatmapVisualColors (legado + preset)', () => {
  it('sem preset mantém as rampas Verde Agro legadas', () => {
    expect(heatmapVisualColors('light', 'theme')).toEqual([...LANDAGRI_SEQUENTIAL_LIGHT]);
    expect(heatmapVisualColors('light', 'divergent')).toEqual([...LANDAGRI_DIVERGENT_LIGHT]);
  });

  it('com preset deriva a rampa do preset ativo', () => {
    expect(heatmapVisualColors('light', 'theme', 'terra')).toEqual(
      sequentialRampForPreset('terra', 'light'),
    );
    expect(heatmapVisualColors('light', 'divergent', 'terra')).toEqual(
      divergentRampForPreset('terra', 'light'),
    );
    expect(heatmapVisualColors('light', 'theme', 'terra')).not.toEqual([
      ...LANDAGRI_SEQUENTIAL_LIGHT,
    ]);
  });
});

describe('builders ECharts seguem o colorway do preset', () => {
  const custom = ['#111111', '#222222', '#333333'];

  it('barra horizontal usa o colorway injetado', () => {
    const option = buildHorizontalBarOption({
      labels: ['A'],
      values: [1],
      theme: 'light',
      locale: 'pt-BR',
      colorway: custom,
    });
    expect(option.color as string[]).toEqual(custom);
    const series = option.series as { itemStyle: { color: string } }[];
    expect(series[0].itemStyle.color).toBe('#111111');
  });

  it('barra horizontal divergente codifica o sinal pelo preset', () => {
    const option = buildHorizontalBarOption({
      labels: ['A', 'B'],
      values: [5, -3],
      theme: 'light',
      locale: 'pt-BR',
      palette: 'divergent',
      preset: 'terra',
    });
    const series = option.series as {
      data: { value: number | null; itemStyle: { color: string } }[];
    }[];
    expect(series[0].data[0].itemStyle.color).toBe('#80400B');
    expect(series[0].data[1].itemStyle.color).toBe(DIVERGENT_NEGATIVE.terra.light);
  });

  it('cor explícita vence a divergência', () => {
    const option = buildHorizontalBarOption({
      labels: ['A'],
      values: [-3],
      theme: 'light',
      locale: 'pt-BR',
      palette: 'divergent',
      preset: 'terra',
      color: '#123456',
    });
    const series = option.series as { itemStyle: { color: string } }[];
    expect(series[0].itemStyle.color).toBe('#123456');
  });

  it('barras agrupadas, linha e pizza usam o colorway injetado', () => {
    const grouped = buildGroupedBarOption({
      categories: ['A'],
      series: [{ name: 'S1', values: [1] }],
      theme: 'dark',
      locale: 'pt-BR',
      colorway: custom,
    });
    expect(grouped.color as string[]).toEqual(custom);

    const line = buildLineOption({
      series: [{ name: 'S1', x: ['A'], y: [1] }],
      theme: 'dark',
      locale: 'pt-BR',
      colorway: custom,
    });
    expect(line.color as string[]).toEqual(custom);

    const pie = buildPieOption({
      slices: [{ label: 'A', value: 1 }],
      theme: 'light',
      locale: 'pt-BR',
      colorway: custom,
    });
    expect(pie.color as string[]).toEqual(custom);
  });

  it('heatmap com preset usa a rampa do preset; sem preset, a legada', () => {
    const input = {
      x: ['A'],
      y: ['B'],
      z: [[1]],
      theme: 'light' as const,
      locale: 'pt-BR',
    };
    const withPreset = buildHeatmapOption({ ...input, preset: 'terra' });
    const visual = withPreset.visualMap as { inRange: { color: string[] } };
    expect(visual.inRange.color).toEqual(sequentialRampForPreset('terra', 'light'));

    const legacy = buildHeatmapOption(input);
    expect((legacy.visualMap as { inRange: { color: string[] } }).inRange.color).toEqual([
      ...LANDAGRI_SEQUENTIAL_LIGHT,
    ]);

    // Override explícito continua vencendo.
    const over = buildHeatmapOption({ ...input, preset: 'terra', colors: ['#000001'] });
    expect((over.visualMap as { inRange: { color: string[] } }).inRange.color).toEqual([
      '#000001',
    ]);
  });

  it('getChartLayout aceita colorway do preset', () => {
    expect(getChartLayout('light').colorway?.[0]).toBe('#2E7D32');
    expect(getChartLayout('light', 'Inter', presetCharts('terra', 'light')).colorway?.[0]).toBe(
      '#80400B',
    );
  });
});

describe('useChartColorway (colorway viva do preset)', () => {
  it('cai no preset da raiz quando as CSS vars estão vazias (jsdom)', () => {
    document.documentElement.dataset.preset = 'terra';
    expect(readChartColorway('light', 'terra')[0]).toBe('#80400B');
    const { result } = renderHook(() => useChartColorway(), { wrapper: themeWrapper });
    expect(result.current.preset).toBe('terra');
    expect(result.current.colorway[0]).toBe('#80400B');
  });
});

describe('useThemeManager palette (sidebar divergente por preset)', () => {
  it('alterna data-palette e densifica a sidebar; reset restaura', () => {
    const { result } = renderHook(() => useThemeManager(), { wrapper: themeWrapper });
    expect(result.current.palette).toBe('theme');
    expect(document.documentElement.dataset.palette).toBe('theme');
    const baseActive = getComputedStyle(document.documentElement).getPropertyValue(
      '--color-sidebar-active-bg',
    );

    act(() => {
      result.current.setPalette('divergent');
    });
    expect(result.current.palette).toBe('divergent');
    expect(document.documentElement.dataset.palette).toBe('divergent');
    expect(localStorage.getItem('landagri-palette')).toBe('divergent');
    const hcActive = getComputedStyle(document.documentElement).getPropertyValue(
      '--color-sidebar-active-bg',
    );
    expect(hcActive).not.toBe(baseActive);

    act(() => {
      result.current.resetCustomizations();
    });
    expect(result.current.palette).toBe('theme');
    expect(document.documentElement.dataset.palette).toBe('theme');
  });
});
