/**
 * Preset-aware chart colors (reversível — só constantes + funções puras).
 *
 * Problema: os builders ECharts (`echarts-options.ts`), `getChartLayout` e
 * os temas ECharts registrados usavam SÓ o colorway Verde Agro v2 por
 * light/dark (`LANDAGRI_COLORWAY_*`), ignorando o preset ativo (Azul,
 * Verde Agro, Terra, Âmbar). O preset já grava `--color-chart-1..10` na
 * raiz (`use-theme-manager` → `applyToRoot`); este módulo deriva rampas e
 * âncoras do preset para que os gráficos sigam o tema ativo.
 *
 * Regra analítica (`palette: 'theme' | 'divergent'`):
 * - `'theme'` (default): séries categóricas e magnitudes/intensidades —
 *   colorway do preset + rampa sequencial neutro → primária do preset.
 * - `'divergent'`: SÓ onde o sinal tem sentido analítico (heatmap de
 *   correlação −1…1, barras de delta em torno de 0). O matiz codifica o
 *   sinal; a claridade, a magnitude. Braço positivo = primária do preset;
 *   braço negativo = âncora complementar por preset (`DIVERGENT_NEGATIVE`)
 *   para manter a divergência legível em qualquer preset.
 *
 * Exceções semânticas intencionais (NÃO seguem o preset — identidade visual):
 * - `LULC_CLASS_COLORS` (types/theme): classe de cobertura = cor fixa.
 * - `phenoColors`: fase fenológica (plantio = verde agro, colheita =
 *   âmbar/terra) — codifica a fase, nunca a cultura/região.
 * - Bordas brancas de fatias (`#fff`) e halo de ênfase: neutros de desenho.
 */
import {
  DEFAULT_PRESET,
  getThemePreset,
} from '../config/theme-presets';
import type { EChartsPilotTheme } from './echarts-theme';

/** Neutro inicial da rampa sequencial por tema (espelha o legado). */
export const SEQUENTIAL_NEUTRAL_LIGHT = '#f1f5f1';
export const SEQUENTIAL_NEUTRAL_DARK = '#233042';

/** Centro neutro (~0) da rampa divergente por tema (espelha o legado). */
export const DIVERGENT_CENTER_LIGHT = '#f7f4ec';
export const DIVERGENT_CENTER_DARK = '#3a4556';

/**
 * Âncora negativa por preset — o matiz do "ruim/negativo".
 *
 * Verde Agro (v1/v2) e Azul divergem do vermelho-terra (semântica agro:
 * crescimento vs. perda); Terra (marrom) diverge do teal e Âmbar do
 * índigo, para que os dois braços não colapsem no mesmo matiz do preset.
 */
export const DIVERGENT_NEGATIVE: Record<string, { light: string; dark: string }> = {
  default: { light: '#b2182b', dark: '#c94a4a' },
  agro: { light: '#b2182b', dark: '#c94a4a' },
  'agro-v2': { light: '#b2182b', dark: '#c94a4a' },
  terra: { light: '#0b5a63', dark: '#3b9aa5' },
  ambar: { light: '#3f4a9e', dark: '#7c83db' },
};

function normalizeHex(hex: string): [number, number, number] | null {
  const m = /^#([0-9a-fA-F]{6})$/.exec(hex.trim());
  if (!m) return null;
  const n = parseInt(m[1], 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

function toHex([r, g, b]: [number, number, number]): string {
  const pad = (v: number): string =>
    Math.max(0, Math.min(255, Math.round(v))).toString(16).padStart(2, '0');
  return `#${pad(r)}${pad(g)}${pad(b)}`;
}

/**
 * Mistura dois hex (`t=0` → `a`, `t=1` → `b`). Fora de [0,1] é fixado.
 * Retorna `#000000` quando alguma ponta não é hex de 6 dígitos.
 */
export function mixHex(a: string, b: string, t: number): string {
  const pa = normalizeHex(a);
  const pb = normalizeHex(b);
  if (!pa || !pb) return '#000000';
  const k = Math.max(0, Math.min(1, t));
  return toHex([
    pa[0] + (pb[0] - pa[0]) * k,
    pa[1] + (pb[1] - pa[1]) * k,
    pa[2] + (pb[2] - pa[2]) * k,
  ]);
}

/** Colorway categórica (10 stops) do preset para o tema — cópia nova. */
export function presetCharts(presetValue: string, theme: EChartsPilotTheme): string[] {
  const preset = getThemePreset(presetValue);
  const colors = theme === 'dark' ? preset.dark.charts : preset.light.charts;
  return [...colors.slice(0, 10)];
}

/** Primária do preset (braço positivo da divergência). */
export function presetPrimary(presetValue: string, theme: EChartsPilotTheme): string {
  const preset = getThemePreset(presetValue);
  return theme === 'dark' ? preset.dark.primary : preset.light.primary;
}

/** Âncora negativa do preset (braço negativo; fallback = vermelho-terra). */
export function presetNegative(presetValue: string, theme: EChartsPilotTheme): string {
  const anchor = DIVERGENT_NEGATIVE[presetValue] ?? DIVERGENT_NEGATIVE[DEFAULT_PRESET];
  return theme === 'dark' ? anchor.dark : anchor.light;
}

/**
 * Rampa sequencial do preset — intensidade/magnitude (neutro → primária).
 * 5 stops; extremidade profunda escurece (light) ou clareia (dark) a
 * primária para manter contraste com o canvas do tema.
 */
export function sequentialRampForPreset(
  presetValue: string,
  theme: EChartsPilotTheme,
): string[] {
  const primary = presetPrimary(presetValue, theme);
  const neutral = theme === 'dark' ? SEQUENTIAL_NEUTRAL_DARK : SEQUENTIAL_NEUTRAL_LIGHT;
  const deep = theme === 'dark' ? mixHex(primary, '#ffffff', 0.3) : mixHex(primary, '#000000', 0.35);
  return [
    neutral,
    mixHex(neutral, primary, 0.35),
    mixHex(neutral, primary, 0.7),
    primary,
    deep,
  ];
}

/**
 * Rampa divergente do preset — sinal com ponto neutro.
 * 5 stops: [negativo, transição, centro (~0), transição, primária].
 */
export function divergentRampForPreset(
  presetValue: string,
  theme: EChartsPilotTheme,
): string[] {
  const positive = presetPrimary(presetValue, theme);
  const negative = presetNegative(presetValue, theme);
  const center = theme === 'dark' ? DIVERGENT_CENTER_DARK : DIVERGENT_CENTER_LIGHT;
  return [
    negative,
    mixHex(negative, center, 0.55),
    center,
    mixHex(center, positive, 0.55),
    positive,
  ];
}

/**
 * Cor divergente por valor — barras de delta em torno de 0.
 * `value < 0` → âncora negativa do preset; `>= 0` → primária do preset.
 * `null` (ausente) → `fallback` (default: cinza neutro do colorway).
 */
export function divergingColorForValue(
  value: number | null,
  presetValue: string,
  theme: EChartsPilotTheme,
  fallback = '#B0BEC5',
): string {
  if (value === null) return fallback;
  return value < 0 ? presetNegative(presetValue, theme) : presetPrimary(presetValue, theme);
}

/**
 * Variante de alto contraste da sidebar para `palette: 'divergent'`.
 *
 * Mantém o matiz do preset, mas densifica o fundo ativo (mistura da
 * primária sobre o fundo da sidebar) e escurece/clareia o texto ativo
 * para leitura AA sobre o fundo densificado. Tudo derivado do preset —
 * nenhum hex novo por preset.
 */
export function sidebarDivergentVars(
  presetValue: string,
  theme: EChartsPilotTheme,
): { sidebarActiveBg: string; sidebarTextActive: string; sidebarHoverBg: string } {
  const preset = getThemePreset(presetValue);
  const colors = theme === 'dark' ? preset.dark : preset.light;
  const activeBg = mixHex(colors.primary, colors.sidebarBg, theme === 'dark' ? 0.62 : 0.72);
  const textActive =
    theme === 'dark'
      ? mixHex(colors.primary, '#ffffff', 0.25)
      : mixHex(colors.primary, '#000000', 0.3);
  const hoverBg = mixHex(colors.primary, colors.sidebarHoverBg, theme === 'dark' ? 0.82 : 0.88);
  return { sidebarActiveBg: activeBg, sidebarTextActive: textActive, sidebarHoverBg: hoverBg };
}
