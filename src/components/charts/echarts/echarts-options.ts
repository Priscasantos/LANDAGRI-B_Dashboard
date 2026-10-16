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
import { translate } from '../../../i18n';
import type { Locale } from '../../../i18n/types';
import {
  BERRY_TOOLTIP_BG,
  GRID_DIVIDER_DARK,
  GRID_DIVIDER_LIGHT,
  LANDAGRI_COLORWAY_DARK,
  LANDAGRI_COLORWAY_LIGHT,
  formatEChartsNumber,
  heatmapVisualColors,
  type EChartsPalette,
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
  /**
   * Explicit palette (default `'theme'`). Categorical builders always use
   * the colorway of the active theme and intentionally ignore `'divergent'`
   * (sign-encoding hues would mislead counts/magnitudes); only
   * `buildHeatmapOption` varies output by palette — `'divergent'` solely
   * for correlation-style −1…1 data.
   */
  palette?: EChartsPalette;
  /**
   * Nome-base do PNG (`toolbox.saveAsImage`) — montado pelo chamador com
   * rota/iniciativa/locale (ver `useChartExport`). Omitido → fallback
   * `landagri-chart-{locale}`.
   */
  exportName?: string;
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
    confine: true,
    padding: [8, 12],
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
    itemGap: 12,
    textStyle: {
      fontSize: LEGEND_FONT_SIZE,
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
    // Contraste AA nos dois temas: slate-500 no light (4.76:1 no branco),
    // slate-400 no dark (~7:1 no canvas escuro).
    labelColor: theme === 'dark' ? '#94a3b8' : '#64748b',
  };
}

function colorwayOf(theme: EChartsPilotTheme): string[] {
  return [...(theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT)];
}

/**
 * Toolbox por gráfico (Expansão #2, reversível): `saveAsImage` (PNG 2x com o
 * `exportName` de rota/iniciativa/locale) + `dataView` somente-leitura.
 * Títulos via i18n (`charts:toolboxSaveAsImage/toolboxDataView`).
 */
export function buildChartToolbox(
  locale: string,
  exportName?: string,
  theme: EChartsPilotTheme = 'light',
): Record<string, unknown> {
  const loc: Locale = locale.startsWith('pt') ? 'pt-BR' : 'en';
  const saveTitle = translate(loc, 'charts', 'toolboxSaveAsImage');
  const viewTitle = translate(loc, 'charts', 'toolboxDataView');
  const closeTitle = translate(loc, 'common', 'close');
  const refreshTitle = translate(loc, 'errors', 'boundaryRetry');
  return {
    show: true,
    orient: 'horizontal',
    right: 8,
    top: 0,
    itemSize: 14,
    iconStyle: { borderColor: theme === 'dark' ? '#94a3b8' : '#64748b' },
    emphasis: { iconStyle: { borderColor: theme === 'dark' ? '#e2e8f0' : '#1e293b' } },
    feature: {
      saveAsImage: {
        show: true,
        title: saveTitle,
        name:
          exportName ??
          `landagri-chart-${locale.startsWith('pt') ? 'pt-br' : 'en'}`,
        type: 'png',
        pixelRatio: 2,
      },
      dataView: {
        show: true,
        title: viewTitle,
        readOnly: true,
        lang: [viewTitle, closeTitle, refreshTitle],
      },
    },
  };
}

/**
 * Escala tipográfica dos charts (passada tipográfica, reversível):
 * - ticks Inter 12px com margem de 8px do eixo;
 * - legendas Inter 12px com wrap bottom;
 * - rótulos de categoria longos truncados na exibição (nome completo no tooltip).
 */
const AXIS_TICK_FONT_SIZE = 12;
const LEGEND_FONT_SIZE = 12;
const AXIS_LABEL_MARGIN = 8;
/** Comprimento máximo de rótulo de categoria exibido (tooltip mostra o nome cheio). */
const MAX_CATEGORY_LABEL = 30;

/** Rótulo de tick padrão: Inter 12px, cor AA do tema, margem do eixo. */
function tickLabel(
  theme: EChartsPilotTheme,
  fontFamily: string,
  extra: Record<string, unknown> = {},
): Record<string, unknown> {
  const { labelColor } = axisCommon(theme);
  return {
    color: labelColor,
    fontSize: AXIS_TICK_FONT_SIZE,
    fontFamily,
    margin: AXIS_LABEL_MARGIN,
    ...extra,
  };
}

/** Trunca rótulos de exibição longos com elipse (tooltip preserva o texto cheio). */
function truncateCategoryLabel(value: unknown, max: number = MAX_CATEGORY_LABEL): string {
  const text = String(value);
  return text.length > max ? `${text.slice(0, max - 1)}…` : text;
}

/**
 * Desbasta eixos de categoria lotados (anos 1985–2024): mostra ~10 rótulos
 * inteiros em vez de 40 sobrepostos. Eixos curtos (≤15 itens) intactos.
 */
function categoryInterval(length: number): number {
  if (length <= 15) return 0;
  return Math.ceil(length / 10) - 1;
}

/**
 * Reserva espaço vertical para a legenda com wrap: 1 linha (56), 2 linhas
 * (80) ou 3+ linhas (104) conforme o nº de séries — sem colidir com o eixo x.
 */
function legendGridBottom(seriesCount: number): number {
  if (seriesCount > 8) return 104;
  if (seriesCount > 4) return 80;
  return 56;
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
  const { divider } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: { ...legendBase(input.theme, fontFamily), show: false },
    grid: { left: 8, right: 24, top: 16, bottom: 8, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: input.labels,
      axisLabel: tickLabel(input.theme, fontFamily),
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
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
    },
    legend: legendBase(input.theme, fontFamily),
    grid: { left: 8, right: 24, top: 40, bottom: legendGridBottom(input.series.length), containLabel: true },
    xAxis: {
      type: 'category',
      data: input.categories,
      axisLabel: tickLabel(input.theme, fontFamily, {
        rotate: 45,
        formatter: (v: unknown): string => truncateCategoryLabel(v),
      }),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    yAxis: {
      type: input.yAxisType ?? 'value',
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
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
                // Linha de referência neutra do tema (AA nos dois temas);
                // override explícito continua vencendo.
                color: input.referenceLine.color ?? labelColor,
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
   * Default: rampa do tema ativo (`palette: 'theme'`); `'divergent'`
   * resolve a paleta divergente verde↔terra/vermelho (correlação −1…1).
   * Override explícito continua vencendo (ex. categorias plantio/colheita).
   */
  colors?: string[];
  /** visualMap bounds (Plotly `zmin`/`zmax` analogue). */
  min?: number;
  max?: number;
  /** Render values inside cells (Plotly `texttemplate` analogue). */
  showValues?: boolean;
  /**
   * Value range rendered on light cells (label usa texto escuro legível;
   * fora dela, branco). Quando omitido, a cor do rótulo é automática por
   * contraste máximo contra a rampa resolvida (AA nos dois temas).
   */
  labelDarkRange?: [number, number];
}

/** Parse `#rgb`/`#rrggbb` → [r, g, b] (0–255); null quando não-hex. */
function parseHexColor(color: string): [number, number, number] | null {
  const m = /^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$/.exec(color.trim());
  if (!m) return null;
  const h = m[1].length === 3 ? m[1].split('').map((c) => c + c).join('') : m[1];
  const n = parseInt(h, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
  const lin = (c: number): number => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  };
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

function contrastRatio(l1: number, l2: number): number {
  const [hi, lo] = l1 >= l2 ? [l1, l2] : [l2, l1];
  return (hi + 0.05) / (lo + 0.05);
}

function mixRgb(
  a: [number, number, number],
  b: [number, number, number],
  t: number,
): [number, number, number] {
  return [
    Math.round(a[0] + (b[0] - a[0]) * t),
    Math.round(a[1] + (b[1] - a[1]) * t),
    Math.round(a[2] + (b[2] - a[2]) * t),
  ];
}

/**
 * Cor do rótulo da célula com contraste máximo (branco Berry `#ffffff`
 * vs. texto escuro `#1e293b`) contra a rampa resolvida na posição do
 * valor. Garante a melhor legibilidade disponível nos dois temas, seja
 * rampa sequencial ou divergente.
 */
function autoCellLabelColor(
  value: number,
  vMin: number,
  vMax: number,
  ramp: string[],
): string {
  const t = vMax > vMin ? Math.max(0, Math.min(1, (value - vMin) / (vMax - vMin))) : 0;
  const stops = ramp.map(parseHexColor).filter((c): c is [number, number, number] => c !== null);
  if (stops.length === 0) return '#ffffff';
  const pos = t * (stops.length - 1);
  const i = Math.min(Math.floor(pos), stops.length - 1);
  const j = Math.min(i + 1, stops.length - 1);
  const bg = relativeLuminance(mixRgb(stops[i], stops[j], pos - i));
  const white = contrastRatio(bg, 1);
  const dark = contrastRatio(bg, relativeLuminance([30, 41, 59]));
  return dark >= white ? '#1e293b' : '#ffffff';
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
  // Rampa do tema ativo por paleta (override explícito vence); rótulo
  // automático por contraste quando `labelDarkRange` é omitido.
  const ramp = input.colors ?? heatmapVisualColors(input.theme, input.palette ?? 'theme');
  const darkRange = input.labelDarkRange;
  const [darkLo, darkHi] = darkRange ?? [vMin, vMin + (vMax - vMin) * 0.4];
  return {
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
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
    grid: { left: 8, right: 24, top: 16, bottom: 104, containLabel: true },
    xAxis: {
      type: 'category',
      data: input.x,
      axisLabel: tickLabel(input.theme, fontFamily, {
        rotate: 45,
        interval: categoryInterval(input.x.length),
        hideOverlap: true,
        formatter: (v: unknown): string => truncateCategoryLabel(v),
      }),
      axisTick: { show: false },
      splitArea: { show: false },
    },
    yAxis: {
      type: 'category',
      data: input.y,
      axisLabel: tickLabel(input.theme, fontFamily),
      axisTick: { show: false },
    },
    visualMap: {
      min: vMin,
      max: vMax,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 8,
      inRange: {
        color: ramp,
      },
      textStyle: { color: labelColor, fontFamily, fontSize: 11 },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: input.showValues ?? false,
          fontSize: 11,
          fontFamily,
          // Halo estático do tema: realça o glifo na faixa de transição da
          // rampa (onde nem branco nem Berry atingem 4.5:1 sozinhos); nos
          // stops o contraste ≥4.5:1 já vem da cor automática (ver teste).
          textBorderWidth: 2,
          textBorderColor: input.theme === 'dark' ? 'rgba(255,255,255,0.85)' : 'rgba(30,41,59,0.85)',
          color: (params: { value?: unknown }): string => {
            const v = Array.isArray(params.value) ? params.value[2] : params.value;
            if (typeof v !== 'number') return '#ffffff';
            if (darkRange !== undefined) return v >= darkLo && v <= darkHi ? '#1e293b' : '#ffffff';
            return autoCellLabelColor(v, vMin, vMax, ramp);
          },
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
  /**
   * Y-axis bounds for 0/1-style series (ex. cobertura temporal binária):
   * omite ticks fracionários como 0.5. Omitidos → eixo automático
   * (comportamento dos demais line charts, inalterado).
   */
  yMin?: number;
  /** Y-axis upper bound (ver `yMin`). */
  yMax?: number;
  /** Y-axis minimum tick gap (ver `yMin`; `1` = só ticks inteiros). */
  yMinInterval?: number;
}

export function buildLineOption(input: LineInput): EChartsCoreOption {
  const { divider } = axisCommon(input.theme);
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
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'axis',
    },
    legend: legendBase(input.theme, fontFamily),
    grid: { left: 8, right: 24, top: 40, bottom: legendGridBottom(input.series.length), containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: xCats,
      axisLabel: tickLabel(input.theme, fontFamily, {
        rotate: 45,
        interval: categoryInterval(xCats.length),
        hideOverlap: true,
        formatter: (v: unknown): string => truncateCategoryLabel(v),
      }),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    yAxis: {
      type: 'value',
      ...(input.yMin !== undefined ? { min: input.yMin } : {}),
      ...(input.yMax !== undefined ? { max: input.yMax } : {}),
      ...(input.yMinInterval !== undefined ? { minInterval: input.yMinInterval } : {}),
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
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
                // Destaque âmbar agro do tema ativo (colorway[6]), não hex fixo.
                itemStyle: { color: s.markPoint.color ?? colorway[6] },
                label: {
                  formatter: s.markPoint.label,
                  fontSize: 11,
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
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
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
          // Fatias <1%: sem rótulo externo (ilegível no arco mínimo);
          // valor segue na legenda + tooltip Berry.
          formatter: (params: { name?: string; percent?: number }): string => {
            const percent = params.percent ?? 0;
            if (percent < 1) return '';
            return `${params.name ?? ''}: ${percent.toFixed(2)}%`;
          },
          color: labelColor,
          fontSize: 12,
          fontFamily,
        },
        // Fatias pequenas: espalha/esconde rótulos sobrepostos em vez de empilhar.
        labelLayout: { hideOverlap: true, moveOverlap: 'shiftY' },
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

/**
 * Declutter de rótulos ENTRE séries (pairwise: 12 séries de 1 ponto com
 * nomes longos): `labelLayout.hideOverlap` só atua dentro de cada série,
 * então o aglomerado vira um blob ilegível. Mantém o rótulo só dos pontos
 * isolados no espaço normalizado (largura estimada pelo texto real);
 * tooltip + legenda preservam todas as identidades. Puro e testável.
 */
function niceCeil(v: number): number {
  if (!(v > 0)) return 0;
  const m = 10 ** Math.floor(Math.log10(v));
  const f = v / m;
  const nf = f <= 1 ? 1 : f <= 2 ? 2 : f <= 2.5 ? 2.5 : f <= 5 ? 5 : 10;
  return nf * m;
}

function declutterScatterLabels(
  series: ScatterSeriesInput[],
  yAxisType: 'value' | 'log' | undefined,
): boolean[][] {
  const ny = (y: number): number =>
    yAxisType === 'log' ? Math.log10(Math.max(y, 1e-9)) : y;
  const pts: { si: number; di: number; x: number; y: number; w: number }[] = [];
  series.forEach((s, si) => {
    if (s.labels === undefined) return;
    s.data.forEach(([x, y], di) => {
      if (typeof x !== 'number' || typeof y !== 'number') return;
      const text = s.labels?.[di] ?? '';
      pts.push({ si, di, x, y: ny(y), w: text.length });
    });
  });
  const visible: boolean[][] = series.map((s) =>
    s.data.map(() => true),
  );
  if (pts.length < 2) return visible;
  const xs = pts.map((p) => p.x);
  const ys = pts.map((p) => p.y);
  // Normaliza pela EXTENSÃO DO EIXO (não pelos dados): eixo `value`
  // inclui o 0 por padrão e arredonda o teto — é essa a densidade real
  // dos rótulos na tela. Eixo log cobre as décadas dos dados.
  const xLo = Math.min(0, Math.min(...xs));
  let xHi = niceCeil(Math.max(...xs));
  if (!(xHi > xLo)) xHi = xLo + 1;
  let yLo: number;
  let yHi: number;
  if (yAxisType === 'log') {
    yLo = Math.floor(Math.min(...ys));
    yHi = Math.ceil(Math.max(...ys));
    if (!(yHi > yLo)) yHi = yLo + 1;
  } else {
    yLo = Math.min(0, Math.min(...ys));
    yHi = niceCeil(Math.max(...ys));
    if (!(yHi > yLo)) yHi = yLo + 1;
  }
  // ~6px por caractere a 10px num plot de ~800px; altura do rótulo ~0.06.
  const norm = pts.map((p) => ({
    ...p,
    nx: (p.x - xLo) / (xHi - xLo),
    nyv: (p.y - yLo) / (yHi - yLo),
    hw: ((p.w * 6) / 800 + 0.03) / 2,
  }));
  // Pontos mais isolados primeiro (maior distância mínima aos demais).
  const order = norm
    .map((p, i) => {
      let d = Infinity;
      norm.forEach((q, j) => {
        if (i === j) return;
        d = Math.min(d, Math.hypot(p.nx - q.nx, (p.nyv - q.nyv) * 2));
      });
      return { i, d };
    })
    .sort((a, b) => b.d - a.d);
  const kept: typeof norm = [];
  for (const { i } of order) {
    const p = norm[i];
    const collides = kept.some(
      (k) => Math.abs(p.nx - k.nx) < p.hw + k.hw && Math.abs(p.nyv - k.nyv) < 0.06,
    );
    if (!collides) kept.push(p);
    else visible[p.si][p.di] = false;
  }
  return visible;
}

export function buildScatterOption(input: ScatterInput): EChartsCoreOption {
  const { divider, labelColor } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const labelVisible = declutterScatterLabels(input.series, input.yAxisType);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    grid: { left: 8, right: 24, top: 40, bottom: legendGridBottom(input.series.length), containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: input.yAxisType ?? 'value',
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
      splitLine: { lineStyle: { color: divider } },
    },
    series: input.series.map((s, i) => {
      const color = s.color ?? colorway[i % colorway.length];
      // Rótulos com declutter cross-series: ponto colado vira datum com
      // `label.show: false` (identidade segue no tooltip + legenda).
      const data =
        s.labels !== undefined
          ? s.data.map(([x, y], di) => ({
              value: [x, y] as [number | string, number | null],
              label: { show: labelVisible[i]?.[di] ?? true },
            }))
          : s.data;
      return {
        type: 'scatter',
        name: s.name,
        data,
        symbolSize:
          s.sizes !== undefined
            ? (_value: unknown, params: { dataIndex: number }): number => {
                const size = s.sizes?.[params.dataIndex];
                return Math.max(8, Math.min(20, size ?? 10));
              }
            : 8,
        // Rótulos colados (pairwise): esconde os sobrepostos, tooltip preserva.
        labelLayout: { hideOverlap: true },
        label:
          s.labels !== undefined
            ? {
                show: true,
                position: 'top',
                distance: 6,
                fontSize: 10,
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
  /**
   * Expansão #4 (reversível): animated frames via the native `timeline`
   * component (play 1985→present, Verde Agro checkpoint). Omitted →
   * static chart, byte-identical to the fatia 2c output.
   */
  animation?: TimelineAnimation;
}

/** First frame of the animated timeline (task: play 1985→present). */
export const TIMELINE_ANIMATION_START = 1985;
/** Default ms per frame of the animated timeline. */
export const TIMELINE_ANIMATION_PLAY_INTERVAL = 1500;

/**
 * Animated playback config for `buildTimelineOption` (Expansão #4).
 * Frames are whole years; per-frame series reuse the static builder
 * filtered to `year <= frame` (existing series, no new chart type).
 */
export interface TimelineAnimation {
  /** First frame year (default `TIMELINE_ANIMATION_START` = 1985). */
  from?: number;
  /** Last frame year (default: current year). */
  to?: number;
  /** ms per frame (default `TIMELINE_ANIMATION_PLAY_INTERVAL`). */
  playInterval?: number;
  /**
   * Start playing immediately (default true). `EChartsTimeline` forces
   * `false` under `prefers-reduced-motion` (no autoplay in that case).
   */
  autoPlay?: boolean;
}

/** Whole-year frames for the animation, normalized to ascending order. */
export function timelineAnimationYears(
  animation: TimelineAnimation | undefined,
): number[] {
  const fallbackTo = new Date().getFullYear();
  const lo = Math.min(animation?.from ?? TIMELINE_ANIMATION_START, animation?.to ?? fallbackTo);
  const hi = Math.max(animation?.from ?? TIMELINE_ANIMATION_START, animation?.to ?? fallbackTo);
  const years: number[] = [];
  for (let y = lo; y <= hi; y++) years.push(y);
  return years;
}

/**
 * Initiative timeline (fatia 2c): one faint connecting line (first→last
 * year) plus one scatter series of year markers per initiative — the
 * ECharts analogue of the Plotly `lines + markers` timeline. Y is the
 * initiative category axis (reversed, like the Plotly version).
 */
export function buildTimelineOption(input: TimelineInput): EChartsCoreOption {
  const { divider } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const labels = input.items.map((item) => item.label);
  const allYears = input.items.flatMap((item) => item.years);
  const min = allYears.length > 0 ? Math.min(...allYears) : 2000;
  const max = allYears.length > 0 ? Math.max(...allYears) : 2025;
  const tips = new Map<string, string>();
  const series: unknown[] = buildTimelineSeries(input.items, colorway, tips);
  const base = {
    color: [...colorway],
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
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
      // Anos inteiros com limites "redondos" (décadas): só geometria do eixo.
      min: Math.floor((min - 1) / 5) * 5,
      max: Math.ceil((max + 1) / 5) * 5,
      minInterval: 1,
      axisLabel: tickLabel(input.theme, fontFamily, {
        // Years are categories in time: never group digits ("2.000").
        formatter: (v: number): string => String(Math.round(v)),
      }),
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: labels,
      inverse: true,
      axisLabel: tickLabel(input.theme, fontFamily),
      axisTick: { show: false },
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    series,
  };
  if (input.animation === undefined) return base as EChartsCoreOption;
  return {
    ...base,
    grid: { left: 8, right: 24, top: 16, bottom: 64, containLabel: true },
    timeline: buildTimelineAnimation(
      input.theme,
      fontFamily,
      input.animation,
      timelineAnimationYears(input.animation),
    ),
    options: timelineAnimationYears(input.animation).map((year) => ({
      series: buildTimelineSeries(input.items, colorway, tips, year),
    })),
  } as EChartsCoreOption;
}

/**
 * Native `timeline` component (Expansão #4): year labels, autoplay with
 * `playInterval`, checkpoint in the theme's Verde Agro lead color.
 */
function buildTimelineAnimation(
  theme: BaseBuilderInput['theme'],
  fontFamily: string,
  animation: TimelineAnimation,
  years: number[],
): Record<string, unknown> {
  const { divider, labelColor } = axisCommon(theme);
  const checkpoint = colorwayOf(theme)[0];
  return {
    axisType: 'category',
    data: years.map(String),
    autoPlay: animation.autoPlay ?? true,
    playInterval: animation.playInterval ?? TIMELINE_ANIMATION_PLAY_INTERVAL,
    loop: true,
    left: 8,
    right: 8,
    bottom: 0,
    lineStyle: { color: divider },
    label: { color: labelColor, fontSize: 12, fontFamily, formatter: '{value}' },
    itemStyle: { color: labelColor },
    checkpointStyle: {
      color: checkpoint,
      borderColor: '#fff',
      borderWidth: 2,
    },
    controlStyle: {
      showPlayBtn: true,
      showPrevBtn: true,
      showNextBtn: true,
      color: labelColor,
      borderColor: labelColor,
    },
    progress: {
      lineStyle: { color: checkpoint },
      itemStyle: { color: checkpoint },
      label: { color: labelColor, fontSize: 12, fontFamily, formatter: '{value}' },
    },
  };
}

/**
 * Static series builder shared by both modes: one faint connecting line
 * (first→last year) plus one scatter series of year markers per
 * initiative. `uptoYear` filters markers to `year <= frame` for the
 * animated frames (existing series, no new chart type).
 */
function buildTimelineSeries(
  items: TimelineItemInput[],
  colorway: string[],
  tips: Map<string, string>,
  uptoYear?: number,
): unknown[] {
  const series: unknown[] = [];
  items.forEach((item, i) => {
    const color = item.color ?? colorway[i % colorway.length];
    const sorted = [...item.years].sort((a, b) => a - b);
    sorted.forEach((year) => {
      tips.set(
        `${item.label}||${year}`,
        item.tip !== undefined ? item.tip(year) : `<b>${item.label}</b><br>${year}`,
      );
    });
    const visible =
      uptoYear === undefined ? sorted : sorted.filter((year) => year <= uptoYear);
    series.push({
      type: 'line',
      silent: true,
      data:
        visible.length > 0
          ? [
              [visible[0], item.label],
              [visible[visible.length - 1], item.label],
            ]
          : [],
      lineStyle: { color, width: 3, opacity: 0.5 },
      symbol: 'none',
    });
    series.push({
      type: 'scatter',
      name: item.label,
      data: visible.map((year) => [year, item.label]),
      symbolSize: 10,
      itemStyle: { color, borderColor: '#fff', borderWidth: 2 },
    });
  });
  return series;
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
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
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
      axisName: { color: labelColor, fontSize: 12, fontFamily },
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
  const { divider } = axisCommon(input.theme);
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  const labels = input.bars.map((b) => b.y);
  const tips = input.bars.map((b, i) => b.tip ?? labels[i]);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
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
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string => {
          // Só índices inteiros válidos — fora disso, vazio (sem "Oct" duplo).
          if (!Number.isInteger(v)) return '';
          const label = input.xLabels[v];
          return label === undefined ? '' : String(label);
        },
      }),
      splitLine: { lineStyle: { color: divider } },
    },
    yAxis: {
      type: 'category',
      data: labels,
      inverse: true,
      axisLabel: tickLabel(input.theme, fontFamily),
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
  const fontFamily = fontOf(input);
  const colorway = colorwayOf(input.theme);
  return {
    color: [...colorway],
    textStyle: { fontFamily },
    toolbox: buildChartToolbox(input.locale, input.exportName, input.theme),
    tooltip: {
      ...tooltipBase(input, fontFamily),
      trigger: 'item',
    },
    legend: legendBase(input.theme, fontFamily),
    polar: {},
    angleAxis: {
      type: 'category',
      data: input.categories,
      axisLabel: tickLabel(input.theme, fontFamily),
      axisLine: { lineStyle: { color: 'rgba(148,163,184,0.3)' } },
    },
    radiusAxis: {
      axisLabel: tickLabel(input.theme, fontFamily, {
        formatter: (v: number): string =>
          formatEChartsNumber(v, input.locale),
      }),
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
