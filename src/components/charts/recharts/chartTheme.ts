/**
 * Shared recharts theme tokens (Fase 2).
 * Uses LANDAGRI-B CSS variables with hex fallbacks so charts follow
 * light/dark theme without hardcoded colors. Reversible: pure constants.
 */
export const CHART_GRID_STROKE = 'var(--color-chart-grid, #e3e8ef)';

export const CHART_TICK_FILL = 'var(--color-chart-text, #1f2937)';

/** Berry tooltip escuro (ambos os temas) — série primária segue Verde Agro. */
export const CHART_TOOLTIP_STYLE: React.CSSProperties = {
  backgroundColor: '#1e293b',
  border: '1px solid rgba(0,0,0,0.1)',
  borderRadius: '8px',
  fontSize: '12px',
  color: '#ffffff',
};

export const CHART_TOOLTIP_LABEL_STYLE: React.CSSProperties = {
  color: '#ffffff',
  fontWeight: 'bold',
};

/** Categorical palette — Verde Agro v2 (mirrors `--color-chart-1..10` in index.css + CATEGORICAL_COLORS). */
export const RECHARTS_PALETTE: readonly string[] = [
  'var(--color-chart-1, #2E7D32)',
  'var(--color-chart-2, #43A047)',
  'var(--color-chart-3, #7CB342)',
  'var(--color-chart-4, #AED581)',
  'var(--color-chart-5, #1B5E20)',
  'var(--color-chart-6, #C2701D)',
  'var(--color-chart-7, #E6A817)',
  'var(--color-chart-8, #0E7C86)',
  'var(--color-chart-9, #5C6BC0)',
  'var(--color-chart-10, #B0BEC5)',
];

export function paletteColor(index: number, override?: string): string {
  if (override) return override;
  return RECHARTS_PALETTE[index % RECHARTS_PALETTE.length];
}
