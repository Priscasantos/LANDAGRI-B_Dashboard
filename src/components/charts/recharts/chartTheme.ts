/**
 * Shared recharts theme tokens (Fase 2).
 * Uses LANDAGRI-B CSS variables with hex fallbacks so charts follow
 * light/dark theme without hardcoded colors. Reversible: pure constants.
 */
export const CHART_GRID_STROKE = 'var(--color-chart-grid, #f3f4f6)';

export const CHART_TICK_FILL = 'var(--color-chart-text, #1f2937)';

export const CHART_TOOLTIP_STYLE: React.CSSProperties = {
  backgroundColor: 'var(--color-canvas, #ffffff)',
  border: '1px solid var(--color-border, #e2e8f0)',
  borderRadius: '12px',
  fontSize: '12px',
};

export const CHART_TOOLTIP_LABEL_STYLE: React.CSSProperties = {
  color: 'var(--color-fg, #1e293b)',
  fontWeight: 'bold',
};

/** Categorical palette — mirrors `CATEGORICAL_COLORS` in types/theme. */
export const RECHARTS_PALETTE: readonly string[] = [
  '#3b82f6',
  '#10b981',
  '#f59e0b',
  '#ef4444',
  '#8b5cf6',
  '#06b6d4',
  '#84cc16',
  '#ec4899',
  '#f97316',
  '#6366f1',
];

export function paletteColor(index: number, override?: string): string {
  if (override) return override;
  return RECHARTS_PALETTE[index % RECHARTS_PALETTE.length];
}
