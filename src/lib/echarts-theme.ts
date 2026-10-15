/**
 * LandAgri ECharts themes (pilot, reversible).
 *
 * Mirrors `getChartLayout` in `src/lib/chartDefaults.ts`:
 * - Verde Agro colorway (light/dark identical palettes)
 * - Berry tooltip chrome (#1e293b light / #334155 dark)
 * - Divider grid #e3e8ef (light)
 *
 * Registered once via `registerLandAgriThemes(echarts)`; components select
 * `landagri-light` / `landagri-dark` from the effective theme.
 */

export type EChartsPilotTheme = 'light' | 'dark';

/** Verde Agro light — espelha `colorway` de `getChartLayout('light')`. */
export const LANDAGRI_COLORWAY_LIGHT: readonly string[] = [
  '#2E7D32',
  '#43A047',
  '#7CB342',
  '#AED581',
  '#1B5E20',
  '#C2701D',
  '#E6A817',
  '#0E7C86',
  '#5C6BC0',
  '#B0BEC5',
];

/** Verde Agro dark — espelha `colorway` de `getChartLayout('dark')`. */
export const LANDAGRI_COLORWAY_DARK: readonly string[] = [
  '#9CCC65',
  '#7CB342',
  '#C5E1A5',
  '#43A047',
  '#E8A04C',
  '#FFCA28',
  '#4DD0E1',
  '#9FA8DA',
  '#B0BEC5',
  '#66BB6A',
];

/** Berry tooltip background per theme (espelha `hoverlabel.bgcolor`). */
export const BERRY_TOOLTIP_BG: Record<EChartsPilotTheme, string> = {
  light: '#1e293b',
  dark: '#334155',
};

/** Divider grid color (light; dark usa slate translúcido). */
export const GRID_DIVIDER_LIGHT = '#e3e8ef';
export const GRID_DIVIDER_DARK = 'rgba(51,65,85,0.5)';

export const ECHARTS_THEME_LIGHT = 'landagri-light';
export const ECHARTS_THEME_DARK = 'landagri-dark';

interface EChartsLike {
  registerTheme(name: string, theme: Record<string, unknown>): void;
}

function buildTheme(theme: EChartsPilotTheme): Record<string, unknown> {
  const isDark = theme === 'dark';
  return {
    color: [...(isDark ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT)],
    backgroundColor: 'transparent',
    textStyle: {
      color: isDark ? '#e2e8f0' : '#475569',
    },
    tooltip: {
      backgroundColor: BERRY_TOOLTIP_BG[theme],
      borderColor: isDark ? '#475569' : 'rgba(0,0,0,0.1)',
      borderWidth: 1,
      textStyle: { color: '#ffffff', fontSize: 12 },
    },
    categoryAxis: {
      axisLine: {
        lineStyle: { color: isDark ? '#334155' : 'rgba(148,163,184,0.3)' },
      },
      axisTick: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#94a3b8', fontSize: 11 },
      splitLine: {
        lineStyle: {
          color: isDark ? GRID_DIVIDER_DARK : GRID_DIVIDER_LIGHT,
        },
      },
    },
    legend: {
      textStyle: { color: isDark ? '#cbd5e1' : '#475569', fontSize: 11 },
    },
  };
}

/**
 * Register `landagri-light` / `landagri-dark` once (idempotent —
 * `registerTheme` sobrescreve o mesmo nome sem erro).
 */
export function registerLandAgriThemes(echarts: EChartsLike): void {
  echarts.registerTheme(ECHARTS_THEME_LIGHT, buildTheme('light'));
  echarts.registerTheme(ECHARTS_THEME_DARK, buildTheme('dark'));
}

/** Theme name for the effective app theme. */
export function echartsThemeName(theme: EChartsPilotTheme): string {
  return theme === 'dark' ? ECHARTS_THEME_DARK : ECHARTS_THEME_LIGHT;
}

/**
 * Locale-aware number formatting (tooltip/axis): `toLocaleString`
 * PT (`pt-BR`: decimal `,` + milhar `.`) / EN (`.` + `,`).
 */
export function formatEChartsNumber(value: number, locale: string): string {
  return value.toLocaleString(locale.startsWith('pt') ? 'pt-BR' : 'en');
}
