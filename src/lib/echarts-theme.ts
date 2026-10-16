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
 *
 * Preset: as constantes legadas abaixo são o fallback agro-v2. Com
 * `presetValue`, `heatmapVisualColors` deriva a rampa do preset ativo
 * (`chart-preset`) — ver `docs/chart-theme-palette.md`.
 */
import {
  divergentRampForPreset,
  sequentialRampForPreset,
} from './chart-preset';

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

/**
 * Paleta explícita dos builders ECharts (`HeatmapInput.palette`).
 * - `theme` (default): rampas derivadas do colorway Verde Agro do tema
 *   ativo — séries categóricas e heatmaps de intensidade/magnitude.
 * - `divergent`: SÓ onde o sinal tem sentido analítico (heatmap de
 *   correlação −1…1). O matiz codifica o sinal; a claridade, a magnitude.
 */
export type EChartsPalette = 'theme' | 'divergent';

/** Rampa sequencial do tema — intensidade/magnitude (neutro → Verde Agro). */
export const LANDAGRI_SEQUENTIAL_LIGHT: readonly string[] = [
  '#f1f5f1',
  '#c5e1a5',
  '#7cb342',
  '#2e7d32',
  '#1b5e20',
];

/** Rampa sequencial do tema adaptada ao canvas escuro (base slate → verde claro). */
export const LANDAGRI_SEQUENTIAL_DARK: readonly string[] = [
  '#233042',
  '#2f4a2c',
  // Mid-stop afinado para AA: `#357a38` dá 5.26:1 com rótulo branco
  // (`#43a047` ficava em 4.43:1 — ver teste de contraste em
  // `src/test/charts/echartsOptions.test.ts`).
  '#357a38',
  '#7cb342',
  '#9ccc65',
];

/**
 * Paleta divergente própria — verde Agro ↔ terra/vermelho.
 *
 * Justificativa: correlação −1…1 precisa de dois matizes (o colorway
 * categórico e a rampa sequencial codificam só magnitude/categoria, sem
 * ponto neutro). Verde (`#1b5e20`/`#9ccc65`) = associação positiva
 * (semântica agro: crescimento); terra/vermelho (`#b2182b`/`#c94a4a`) =
 * associação negativa; centro neutro (`#f7f4ec`/`#3a4556`) = ~0.
 * Endpoints saturados nos dois temas para manter rótulos brancos com
 * contraste AA; o centro claro (light) usa texto escuro Berry.
 */
export const LANDAGRI_DIVERGENT_LIGHT: readonly string[] = [
  '#b2182b',
  '#e8a04c',
  '#f7f4ec',
  '#7cb342',
  '#1b5e20',
];

/** Variante escura da divergente (endpoints saturados → texto branco AA). */
export const LANDAGRI_DIVERGENT_DARK: readonly string[] = [
  '#c94a4a',
  '#e8a04c',
  '#3a4556',
  '#7cb342',
  '#9ccc65',
];

/** Resolve a rampa do visualMap para o tema + paleta ativos.
 *
 * Sem `presetValue` (default): constantes Verde Agro legadas — caminho
 * puro/estável para testes e para chamadores sem contexto de preset.
 * Com `presetValue`: rampa derivada do preset ativo (`chart-preset`), de
 * modo que Terra/Âmbar/Azul também tingem heatmaps e visualMaps.
 */
export function heatmapVisualColors(
  theme: EChartsPilotTheme,
  palette: EChartsPalette = 'theme',
  presetValue?: string,
): string[] {
  if (presetValue !== undefined) {
    return palette === 'divergent'
      ? divergentRampForPreset(presetValue, theme)
      : sequentialRampForPreset(presetValue, theme);
  }
  if (palette === 'divergent') {
    return [...(theme === 'dark' ? LANDAGRI_DIVERGENT_DARK : LANDAGRI_DIVERGENT_LIGHT)];
  }
  return [...(theme === 'dark' ? LANDAGRI_SEQUENTIAL_DARK : LANDAGRI_SEQUENTIAL_LIGHT)];
}

/** Célula vazia de heatmap categórico (0=ausente) por tema — neutro AA. */
export const HEATMAP_EMPTY_CELL_LIGHT = '#f3f4f6';
export const HEATMAP_EMPTY_CELL_DARK = '#263242';

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
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 12 },
      splitLine: { show: false },
    },
    valueAxis: {
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: isDark ? '#94a3b8' : '#64748b', fontSize: 12 },
      splitLine: {
        lineStyle: {
          color: isDark ? GRID_DIVIDER_DARK : GRID_DIVIDER_LIGHT,
        },
      },
    },
    legend: {
      textStyle: { color: isDark ? '#cbd5e1' : '#475569', fontSize: 12 },
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
