/**
 * Pure ECharts option builders (Fase 2 — no React here).
 *
 * Chrome mirrors `buildStandardLayout`/`getChartLayout`:
 * - Tooltip Berry (#1e293b light / #334155 dark), white 12px text
 * - Legend bottom, square 8px markers (`icon: 'rect'`, item 8×8)
 * - Grid on the divider neutral #e3e8ef (light)
 * - Font via `fontFamily` input (wrappers pass the reactive
 *   `useChartFontFamily()` so charts inherit the active font;
 *   defaults to `CHART_FONT_FAMILY` for pure/test use)
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
  /**
   * Active chart font — wrappers pass `useChartFontFamily()` so charts
   * inherit Inter/Sora/Mono/sistema from the customizer. Defaults to
   * `CHART_FONT_FAMILY` (pure/test use).
   */
  fontFamily?: string;
}

function fontOf(input: BaseBuilderInput): string {
  return input.fontFamily ?? CHART_FONT_FAMILY;
}

function baseText(locale: string): {
  fontFamily: string;
  locale: string;
} {
  return { fontFamily: CHART_FONT_FAMILY, locale };
}

function tooltipBase(
  input: BaseBuilderInput,
  fontFamily: string = fontOf(input),
): Record<string, unknown> {
  void baseText(input.locale);
  return {
    trigger: 'item',
    backgroundColor: BERRY_TOOLTIP_BG[input.theme],
    borderColor: input.theme === 'dark' ? '#475569' : 'rgba(0,0,0,0.1)',
    borderWidth: 1,
    textStyle: { color: '#ffffff', fontSize: 12, fontFamily },
    valueFormatter: (value: number | string): string =>
      typeof value === 'number'
        ? formatEChartsNumber(value, input.locale)
        : String(value),
  };
}

function legendBase(
  theme: EChartsPilotTheme,
  fontFamily: string,
): Record<string, unknown> {
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
      fontFamily,
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

function colorwayOf(theme: EChartsPilotTheme): string[] {
  return [...(theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT)];
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
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: { ...legendBase(input.theme, fontFamily), show: false },
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

export interface GroupedBarSeriesInput {
  name: string;
  values: (number | null)[];
  /** Series color; default = Verde Agro colorway by index. */
  color?: string;
}

export interface GroupedBarInput extends BaseBuilderInput {
  categories: (string | number)[];
  series: GroupedBarSeriesInput[];
  /** Stack all series (Plotly `barmode: 'stack'` analogue, default false). */
  stacked?: boolean;
  /**
   * Dashed average line on the first series (Plotly average `shape`/`trace`
   * analogue). Caller resolves the label via i18n.
   */
  referenceLine?: { value: number; name: string; color?: string };
  /** Y axis scale (Plotly `type: 'log'` analogue for resolution meters). */
  yAxisType?: 'value' | 'log';
}

export function buildGroupedBarOption(
  input: GroupedBarInput,
): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: legendBase(input.theme, fontFamily),
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
      type: input.yAxisType ?? 'value',
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      },
      splitLine: { lineStyle: { color: divider } },
    },
    series: input.series.map((s, idx) => ({
      type: 'bar',
      name: s.name,
      data: s.values,
      itemStyle: {
        color: s.color ?? colorway[idx % colorway.length],
      },
      ...(input.stacked === true ? { stack: 'total' } : {}),
      ...(input.referenceLine !== undefined && idx === 0
        ? {
            markLine: {
              silent: true,
              symbol: 'none',
              lineStyle: {
                color: input.referenceLine.color ?? '#ef4444',
                width: 2,
                type: 'dashed',
              },
              label: {
                formatter: input.referenceLine.name,
                fontSize: 11,
                fontFamily,
              },
              data: [
                {
                  yAxis: input.referenceLine.value,
                  name: input.referenceLine.name,
                },
              ],
            },
          }
        : {}),
    })),
  } as EChartsCoreOption;
}

export interface HeatmapInput extends BaseBuilderInput {
  x: (string | number)[];
  y: (string | number)[];
  z: (number | null)[][];
  /**
   * visualMap `inRange` colors (Plotly `colorscale` analogue).
   * Defaults to the amber intensity ramp.
   */
  colors?: string[];
  /** visualMap bounds (Plotly `zmin`/`zmax` analogue). */
  min?: number;
  max?: number;
  /** Render values inside cells (Plotly `texttemplate` analogue). */
  showValues?: boolean;
}

export function buildHeatmapOption(input: HeatmapInput): EChartsCoreOption {
  const { labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const data: [number, number, number | null][] = [];
  input.z.forEach((row, yi) => {
    row.forEach((v, xi) => {
      data.push([xi, yi, v]);
    });
  });
  const flat = input.z.flat().filter((v): v is number => v !== null);
  const max = flat.length > 0 ? Math.max(...flat) : 0;
  const vMin = input.min ?? 0;
  const vMax = input.max ?? Math.max(max, 1);
  return {
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
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
      min: vMin,
      max: vMax,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 0,
      inRange: {
        color: input.colors ?? ['#f3f4f6', '#fef3c7', '#f97316', '#dc2626', '#7f1d1d'],
      },
      textStyle: { color: labelColor, fontFamily },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: input.showValues ?? false,
          fontSize: 10,
          fontFamily,
          color: '#ffffff',
          formatter: (params: { value?: unknown }): string => {
            const v = Array.isArray(params.value) ? params.value[2] : params.value;
            return typeof v === 'number' ? v.toFixed(2) : '';
          },
        },
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' },
        },
      },
    ],
  } as EChartsCoreOption;
}

export interface EChartsLinePoint {
  name: string;
  x: (string | number)[];
  y: (number | null)[];
  color?: string;
  /** Dashed/dotted average line (Plotly `dash` analogue). */
  dash?: 'solid' | 'dash' | 'dot';
  /** Pinned annotation (Plotly `annotations` analogue for the peak year). */
  markPoint?: { x: string | number; label: string; color?: string };
}

export interface LineInput extends BaseBuilderInput {
  series: EChartsLinePoint[];
  /** Show point markers (Plotly `showMarkers`, default true). */
  showMarkers?: boolean;
  /** Fill under the line (Plotly `fill="tozeroy"`, default false). */
  areaFill?: boolean;
  /** Stack all series (Plotly `stackgroup` analogue, default false). */
  stack?: boolean;
}

export function buildLineOption(input: LineInput): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const showMarkers = input.showMarkers ?? true;
  // Union of x values in first-appearance order — integer years stay
  // whole categories (never fractional labels like "2020.5").
  const xCats: (string | number)[] = [];
  for (const s of input.series) {
    for (const x of s.x) {
      if (!xCats.includes(x)) xCats.push(x);
    }
  }
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
    },
    legend: legendBase(input.theme, fontFamily),
    grid: { left: 8, right: 24, top: 40, bottom: 48, containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xCats,
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
    series: input.series.map((s, i) => {
      const color = s.color ?? colorway[i % colorway.length];
      const markIdx =
        s.markPoint !== undefined ? s.x.indexOf(s.markPoint.x) : -1;
      return {
        type: 'line',
        name: s.name,
        data: xCats.map((cat) => {
          const idx = s.x.indexOf(cat);
          return idx >= 0 ? s.y[idx] : null;
        }),
        lineStyle: {
          width: 2,
          color,
          ...(s.dash === 'dash'
            ? { type: 'dashed' }
            : s.dash === 'dot'
              ? { type: 'dotted' }
              : {}),
        },
        itemStyle: { color },
        symbol: showMarkers ? 'circle' : 'none',
        symbolSize: 6,
        connectNulls: true,
        ...(input.stack === true ? { stack: 'total' } : {}),
        ...(input.areaFill === true || input.stack === true
          ? { areaStyle: { opacity: input.stack === true ? 0.35 : 0.12 } }
          : {}),
        ...(s.markPoint !== undefined && markIdx >= 0
          ? {
              markPoint: {
                symbol: 'pin',
                symbolSize: 36,
                itemStyle: { color: s.markPoint.color ?? '#f59e0b' },
                label: {
                  formatter: s.markPoint.label,
                  fontSize: 10,
                  fontFamily,
                },
                data: [
                  {
                    name: s.markPoint.label,
                    coord: [s.markPoint.x, s.y[markIdx]],
                  },
                ],
              },
            }
          : {}),
      };
    }),
  } as EChartsCoreOption;
}

export interface PieSliceInput {
  label: string;
  value: number;
  color?: string;
}

export interface PieInput extends BaseBuilderInput {
  slices: PieSliceInput[];
  /** Donut hole (Plotly `donut`, default false). */
  donut?: boolean;
}

export function buildPieOption(input: PieInput): EChartsCoreOption {
  const { labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    series: [
      {
        type: 'pie',
        radius: input.donut === true ? ['40%', '68%'] : '65%',
        center: ['50%', '46%'],
        data: input.slices.map((s, i) => ({
          name: s.label,
          value: s.value,
          itemStyle: { color: s.color ?? colorway[i % colorway.length] },
        })),
        label: {
          formatter: '{b}: {d}%',
          color: labelColor,
          fontSize: 11,
          fontFamily,
        },
        labelLine: { lineStyle: { color: 'rgba(148,163,184,0.5)' } },
        itemStyle: { borderColor: '#fff', borderWidth: 2 },
        emphasis: {
          itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.4)' },
        },
      },
    ],
  } as EChartsCoreOption;
}

export interface ScatterSeriesInput {
  name: string;
  /** [x, y] pairs (x may be categorical). */
  data: [number | string, number | null][];
  color?: string;
  /** Per-point bubble size (Plotly `marker.size` analogue, clamped 8–20). */
  sizes?: (number | null)[];
  /** Per-point label above the marker (Plotly `text` analogue). */
  labels?: (string | null)[];
}

export interface ScatterInput extends BaseBuilderInput {
  series: ScatterSeriesInput[];
  /** Y axis scale (Plotly `type: 'log'` analogue, default 'value'). */
  yAxisType?: 'value' | 'log';
}

export function buildScatterOption(input: ScatterInput): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    grid: { left: 8, right: 24, top: 40, bottom: 48, containLabel: true },
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
      type: input.yAxisType ?? 'value',
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      },
      splitLine: { lineStyle: { color: divider } },
    },
    series: input.series.map((s, i) => {
      const color = s.color ?? colorway[i % colorway.length];
      return {
        type: 'scatter',
        name: s.name,
        data: s.data,
        symbolSize:
          s.sizes !== undefined
            ? (_value: unknown, params: { dataIndex: number }): number => {
                const size = s.sizes?.[params.dataIndex];
                return Math.max(8, Math.min(20, size ?? 10));
              }
            : 8,
        label:
          s.labels !== undefined
            ? {
                show: true,
                position: 'top',
                distance: 6,
                fontSize: 9,
                color: labelColor,
                fontFamily,
                formatter: (params: { dataIndex: number }): string =>
                  s.labels?.[params.dataIndex] ?? '',
              }
            : { show: false },
        itemStyle: {
          color,
          borderColor: '#fff',
          borderWidth: 1,
        },
      };
    }),
  } as EChartsCoreOption;
}

export interface TimelineItemInput {
  label: string;
  years: number[];
  color?: string;
  /** Pre-formatted HTML tooltip body; defaults to `<b>label</b><br>year`. */
  tip?: (year: number) => string;
}

export interface TimelineInput extends BaseBuilderInput {
  items: TimelineItemInput[];
}

/**
 * Initiative timeline (fatia 2c): one faint connecting line (first→last
 * year) plus one scatter series of year markers per initiative — the
 * ECharts analogue of the Plotly `lines + markers` timeline. Y is the
 * initiative category axis (reversed, like the Plotly version).
 */
export function buildTimelineOption(input: TimelineInput): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const labels = input.items.map((item) => item.label);
  const allYears = input.items.flatMap((item) => item.years);
  const min = allYears.length > 0 ? Math.min(...allYears) : 2000;
  const max = allYears.length > 0 ? Math.max(...allYears) : 2025;
  const tips = new Map<string, string>();
  const series: unknown[] = [];
  input.items.forEach((item, i) => {
    const color = item.color ?? colorway[i % colorway.length];
    const sorted = [...item.years].sort((a, b) => a - b);
    sorted.forEach((year) => {
      tips.set(
        `${item.label}||${year}`,
        item.tip !== undefined ? item.tip(year) : `<b>${item.label}</b><br>${year}`,
      );
    });
    series.push({
      type: 'line',
      silent: true,
      data:
        sorted.length > 0
          ? [
              [sorted[0], item.label],
              [sorted[sorted.length - 1], item.label],
            ]
          : [],
      lineStyle: { color, width: 3, opacity: 0.5 },
      symbol: 'none',
    });
    series.push({
      type: 'scatter',
      name: item.label,
      data: sorted.map((year) => [year, item.label]),
      symbolSize: 10,
      itemStyle: { color, borderColor: '#fff', borderWidth: 2 },
    });
  });
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
      formatter: (params: {
        seriesName?: string;
        value?: unknown;
      }): string => {
        const value = Array.isArray(params.value) ? params.value[0] : '';
        const key = `${params.seriesName ?? ''}||${String(value)}`;
        return tips.get(key) ?? `<b>${params.seriesName ?? ''}</b><br>${String(value)}`;
      },
    },
    legend: { ...legendBase(input.theme, fontFamily), show: false },
    grid: { left: 8, right: 24, top: 16, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      min: min - 1,
      max: max + 1,
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        // Years are categories in time: never group digits ("2.000").
        formatter: (v: number): string => String(Math.round(v)),
      },
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: labels,
      inverse: true,
      axisLabel: { color: labelColor, fontSize: 11 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    series,
  } as EChartsCoreOption;
}

export interface RadarSeriesInput {
  name: string;
  values: (number | null)[];
  color?: string;
}

export interface RadarInput extends BaseBuilderInput {
  indicators: string[];
  series: RadarSeriesInput[];
}

export function buildRadarOption(input: RadarInput): EChartsCoreOption {
  const { labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const maxPerIndicator = input.indicators.map((_, i) => {
    const vals = input.series
      .map((s) => s.values[i])
      .filter((v): v is number => typeof v === 'number');
    return Math.max(1, ...(vals.length > 0 ? vals : [0]));
  });
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    radar: {
      indicator: input.indicators.map((name, i) => ({
        name,
        max: maxPerIndicator[i],
      })),
      axisName: { color: labelColor, fontSize: 11, fontFamily },
      splitLine: {
        lineStyle: {
          color:
            input.theme === 'dark' ? GRID_DIVIDER_DARK : GRID_DIVIDER_LIGHT,
        },
      },
      splitArea: { show: false },
    },
    series: [
      {
        type: 'radar',
        data: input.series.map((s, i) => {
          const color = s.color ?? colorway[i % colorway.length];
          return {
            name: s.name,
            value: s.values,
            lineStyle: { width: 2, color },
            itemStyle: { color },
            symbolSize: 6,
            areaStyle: { opacity: 0.12 },
          };
        }),
      },
    ],
  } as EChartsCoreOption;
}

export interface GanttBarInput {
  /** Category label (y axis). */
  y: string;
  /** Start offset on the x value axis (Plotly `base` analogue). */
  start: number;
  /** Bar length (Plotly `end - start` analogue). */
  duration: number;
  /** Bar color; default = Verde Agro colorway by index. */
  color?: string;
  /** Legend name; defaults to the y label. */
  name?: string;
  /** Pre-formatted HTML tooltip body (i18n resolved by the caller). */
  tip?: string;
}

export interface GanttInput extends BaseBuilderInput {
  /** Month (or period) labels shown on the x value axis. */
  xLabels: (string | number)[];
  bars: GanttBarInput[];
}

/**
 * Gantt via stacked horizontal bars (fatia 2b spike): a silent transparent
 * `base` series offsets each bar, the `duration` series draws it — the
 * ECharts analogue of Plotly `bar.base`.
 */
export function buildGanttOption(input: GanttInput): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const labels = input.bars.map((b) => b.y);
  const tips = input.bars.map((b, i) => b.tip ?? labels[i]);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
      formatter: (params: { dataIndex?: number }): string =>
        tips[params.dataIndex ?? 0] ?? '',
    },
    legend: { ...legendBase(input.theme, fontFamily), show: false },
    grid: { left: 8, right: 24, top: 16, bottom: 48, containLabel: true },
    xAxis: {
      type: 'value',
      min: -0.5,
      max: Math.max(input.xLabels.length - 0.5, 0.5),
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string => {
          const label = input.xLabels[Math.round(v)];
          return label === undefined ? '' : String(label);
        },
      },
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: labels,
      inverse: true,
      axisLabel: { color: labelColor, fontSize: 11 },
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    series: [
      {
        type: 'bar',
        stack: 'gantt',
        silent: true,
        data: input.bars.map((b) => b.start),
        itemStyle: { color: 'transparent', borderColor: 'transparent' },
      },
      {
        type: 'bar',
        stack: 'gantt',
        data: input.bars.map((b, i) => ({
          value: b.duration,
          name: b.name ?? b.y,
          itemStyle: {
            color: b.color ?? colorway[i % colorway.length],
            borderColor: '#ffffff',
            borderWidth: 1,
          },
        })),
        barWidth: '60%',
      },
    ],
  } as EChartsCoreOption;
}

export interface PolarSeriesInput {
  name: string;
  r: (number | null)[];
  color?: string;
}

export interface PolarInput extends BaseBuilderInput {
  /** Angle-axis categories (Plotly `theta` analogue). */
  categories: (string | number)[];
  series: PolarSeriesInput[];
}

/**
 * Seasonal radar-style polar (fatia 2b spike): `line` series on `polar`
 * coordinates — the ECharts analogue of Plotly `scatterpolar`.
 */
export function buildPolarOption(input: PolarInput): EChartsCoreOption {
  const { labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    polar: {},
    angleAxis: {
      type: 'category',
      data: input.categories,
      axisLabel: { color: labelColor, fontSize: 11, fontFamily },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    radiusAxis: {
      axisLabel: {
        color: labelColor,
        fontSize: 11,
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      },
    },
    series: input.series.map((s, i) => {
      const color = s.color ?? colorway[i % colorway.length];
      return {
        type: 'line',
        coordinateSystem: 'polar',
        name: s.name,
        data: s.r,
        lineStyle: { width: 2, color },
        itemStyle: { color },
        symbol: 'circle',
        symbolSize: 6,
        connectNulls: true,
        areaStyle: { opacity: 0.12 },
      };
    }),
  } as EChartsCoreOption;
}
