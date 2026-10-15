/**
 * Pure ECharts option builders (pilot, reversible — no React here).
 *
 * Chrome mirrors `buildStandardLayout`/`getChartLayout`:
 * - Tooltip Berry (#1e293b light / #334155 dark), white 12px text
 * - Legend bottom, square 8px markers (`icon: 'rect'`, item 8×8)
 * - Grid on the divider neutral #e3e8ef (light)
 * - Font `CHART_FONT_FAMILY` from `src/lib/fonts.ts`
 * - Value/axis formatters per locale via `formatEChartsNumber`
 */
import type { EChartsCoreOption } from 'echarts/core';
import { CHART_FONT_FAMILY } from '../../../lib/fonts';
import {
  BERRY_TOOLTIP_BG,
  GRID_DIVIDER_DARK,
  GRID_DIVIDER_LIGHT,
  LANDAGRI_COLORWAY_DARK,
  LANDAGRI_COLORWAY_LIGHT,
  formatEChartsNumber,
  type EChartsPilotTheme,
} from '../../../lib/echarts-theme';

interface BaseBuilderInput {
  theme: EChartsPilotTheme;
  locale: string;
}

function baseText(locale: string): {
  fontFamily: string;
  locale: string;
} {
  return { fontFamily: CHART_FONT_FAMILY, locale };
}

function tooltipBase(
  input: BaseBuilderInput,
): Record<string, unknown> {
  void baseText(input.locale);
  return {
    trigger: 'item',
    backgroundColor: BERRY_TOOLTIP_BG[input.theme],
    borderColor: input.theme === 'dark' ? '#475569' : 'rgba(0,0,0,0.1)',
    borderWidth: 1,
    textStyle: { color: '#ffffff', fontSize: 12, fontFamily: CHART_FONT_FAMILY },
    valueFormatter: (value: number | string): string =>
      typeof value === 'number'
        ? formatEChartsNumber(value, input.locale)
        : String(value),
  };
}

function legendBase(theme: EChartsPilotTheme): Record<string, unknown> {
  return {
    bottom: 0,
    left: 'center',
    orient: 'horizontal',
    icon: 'rect',
    itemWidth: 8,
    itemHeight: 8,
    textStyle: {
      fontSize: 11,
      color: theme === 'dark' ? '#cbd5e1' : '#475569',
      fontFamily: CHART_FONT_FAMILY,
    },
  };
}

function axisCommon(theme: EChartsPilotTheme): {
  divider: string;
  labelColor: string;
} {
  return {
    divider: theme === 'dark' ? GRID_DIVIDER_DARK : GRID_DIVIDER_LIGHT,
    labelColor: '#94a3b8',
  };
}

export interface HorizontalBarInput extends BaseBuilderInput {
  labels: (string | number)[];
  values: (number | null)[];
  /** Series color; default = first Verde Agro colorway entry. */
  color?: string;
  name?: string;
}

export function buildHorizontalBarOption(
  input: HorizontalBarInput,
): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const colorway = input.theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;
  return {
    color: [...colorway],
    textStyle: { fontFamily: CHART_FONT_FAMILY },
    tooltip: {
      ...tooltipBase(input),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: { ...legendBase(input.theme), show: false },
    grid: { left: 8, right: 24, top: 16, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      },
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: input.labels,
      axisLabel: { color: labelColor, fontSize: 11 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    series: [
      {
        type: 'bar',
        name: input.name ?? '',
        data: input.values,
        itemStyle: { color: input.color ?? colorway[0] },
      },
    ],
  } as EChartsCoreOption;
}

export interface GroupedBarInput extends BaseBuilderInput {
  categories: (string | number)[];
  series: { name: string; values: (number | null)[] }[];
}

export function buildGroupedBarOption(
  input: GroupedBarInput,
): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const colorway = input.theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;
  return {
    color: [...colorway],
    textStyle: { fontFamily: CHART_FONT_FAMILY },
    tooltip: {
      ...tooltipBase(input),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: legendBase(input.theme),
    grid: { left: 8, right: 24, top: 40, bottom: 48, containLabel: true },
    xAxis: {
      type: 'category',
      data: input.categories,
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        rotate: 45,
      },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      },
      splitLine: { lineStyle: { color: divider } },
    },
    series: input.series.map((s) => ({
      type: 'bar',
      name: s.name,
      data: s.values,
    })),
  } as EChartsCoreOption;
}

export interface HeatmapInput extends BaseBuilderInput {
  x: (string | number)[];
  y: (string | number)[];
  z: (number | null)[][];
}

export function buildHeatmapOption(input: HeatmapInput): EChartsCoreOption {
  const { labelColor } = axisCommon(input.theme);
  const data: [number, number, number | null][] = [];
  input.z.forEach((row, yi) => {
    row.forEach((v, xi) => {
      data.push([xi, yi, v]);
    });
  });
  const flat = input.z.flat().filter((v): v is number => v !== null);
  const max = flat.length > 0 ? Math.max(...flat) : 0;
  return {
    textStyle: { fontFamily: CHART_FONT_FAMILY },
    tooltip: {
      ...tooltipBase(input),
      trigger: 'item',
      valueFormatter: (value: unknown): string => {
        const v = Array.isArray(value) ? value[2] : value;
        return typeof v === 'number'
          ? formatEChartsNumber(v, input.locale)
          : String(v ?? '');
      },
    },
    legend: { show: false },
    grid: { left: 8, right: 24, top: 16, bottom: 48, containLabel: true },
    xAxis: {
      type: 'category',
      data: input.x,
      axisLabel: { color: labelColor, fontSize: 11, rotate: 45 },
      axisTick: { show: false },
      splitArea: { show: false },
    },
    yAxis: {
      type: 'category',
      data: input.y,
      axisLabel: { color: labelColor, fontSize: 11 },
      axisTick: { show: false },
    },
    visualMap: {
      min: 0,
      max: Math.max(max, 1),
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: ['#f3f4f6', '#fef3c7', '#f97316', '#dc2626', '#7f1d1d'],
      },
      textStyle: { color: labelColor, fontFamily: CHART_FONT_FAMILY },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' },
        },
      },
    ],
  } as EChartsCoreOption;
}
