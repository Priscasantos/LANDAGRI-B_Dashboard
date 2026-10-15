/**
 * Font options — stacks CSS + Google Fonts `<link>` no `index.html`
 * (display=swap, sem binários no repo). Refs:
 * - Google Fonts Inter: https://fonts.google.com/specimen/Inter
 * - Pairings Sora+Inter: https://fontpair.co/all
 * - Legibilidade (pesos/line-height): https://www.smashingmagazine.com/2020/07/css-techniques-legibility/
 *
 * Papéis: `display` (Sora) para H1/cards KPI — tracking -0.02em,
 * line-height 1.1–1.25; `sans` (Inter 400/500/600) para corpo —
 * line-height 1.5–1.6; `mono` (JetBrains Mono) para números/código
 * com `tabular-nums`. Aplicado via `--font-sans`/`--font-display`/
 * `--font-mono` na raiz + `data-font`. Reversível via customizer reset.
 */
export interface FontOption {
  value: string;
  label: string;
  /** Corpo/UI — Inter com fallbacks de sistema. */
  sans: string;
  /** Títulos/KPI — Sora com fallback para o stack sans. */
  display: string;
  /** Números/código — JetBrains Mono com fallbacks. */
  mono: string;
}

const SYSTEM_SANS =
  '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
const DISPLAY_SANS =
  '"Sora", "Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
const SYSTEM_MONO = '"JetBrains Mono", "Fira Code", ui-monospace, monospace';

export const FONT_OPTIONS: readonly FontOption[] = [
  {
    value: 'default',
    label: 'Padrão',
    sans: SYSTEM_SANS,
    display: DISPLAY_SANS,
    mono: SYSTEM_MONO,
  },
  {
    value: 'mono',
    label: 'Mono (dados)',
    sans: SYSTEM_MONO,
    display: SYSTEM_MONO,
    mono: SYSTEM_MONO,
  },
  {
    value: 'system',
    label: 'Sistema',
    sans: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    display: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, monospace',
  },
];

export function getFontOption(value: string): FontOption {
  return FONT_OPTIONS.find((f) => f.value === value) ?? FONT_OPTIONS[0];
}

/**
 * Stack única dos gráficos (Plotly precisa de string concreta, não
 * `var()`). Espelha o `sans` padrão — Inter via Google Fonts link.
 * Para Mono/Sistema, use `resolveChartFontFamily()` (lê o `data-font`
 * atual da raiz): Recharts herda o CSS da página automaticamente, mas o
 * Plotly precisa da string resolvida no momento do `buildStandardLayout`/
 * `getChartLayout`. Limitação documentada: a fonte do Plotly é capturada
 * na construção do layout — trocar a fonte no customizer refaz o layout
 * no próximo render (recharts acompanha via CSS sem rebuild).
 */
export const CHART_FONT_FAMILY: string = SYSTEM_SANS;

/**
 * Resolve a família de fonte dos gráficos para a opção `value`
 * (`default`/`mono`/`system`); sem argumento, lê o `data-font` vigente
 * na raiz. Retorna sempre o `sans` resolvido (nunca `var()` cru).
 */
export function resolveChartFontFamily(value?: string): string {
  if (value) return getFontOption(value).sans;
  if (typeof document !== 'undefined') {
    const current = document.documentElement.dataset.font;
    if (current) return getFontOption(current).sans;
  }
  return CHART_FONT_FAMILY;
}
