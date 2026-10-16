/**
 * Theme-data palette — single source of truth for chart colors (Fase 2).
 *
 * Entries are CSS `var()` tokens with hex fallbacks, so charts follow the
 * light/dark theme defined in `src/index.css` (`@theme --color-chart-*`)
 * without hardcoding hex inside components. Reversible: pure constants.
 */

/** Categorical palette — mirrors `CATEGORICAL_COLORS` in types/theme (Verde Agro v2). */
export const THEME_DATA_PALETTE: readonly string[] = [
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

/** Diverging scale — mirrors `DIVERGING_COLORS` in types/theme. */
export const THEME_DATA_DIVERGING: readonly string[] = [
  'var(--color-chart-div-1, #d73027)',
  'var(--color-chart-div-2, #fc8d59)',
  'var(--color-chart-div-3, #fee08b)',
  'var(--color-chart-div-4, #d9ef8b)',
  'var(--color-chart-div-5, #91cf60)',
  'var(--color-chart-div-6, #1a9850)',
];

/** Sequential scale — mirrors `SEQUENTIAL_COLORS` in types/theme. */
export const THEME_DATA_SEQUENTIAL: readonly string[] = [
  'var(--color-chart-seq-1, #f7fcf0)',
  'var(--color-chart-seq-2, #e0f3db)',
  'var(--color-chart-seq-3, #ccebc5)',
  'var(--color-chart-seq-4, #a8ddb5)',
  'var(--color-chart-seq-5, #7bccc4)',
  'var(--color-chart-seq-6, #4eb3d3)',
  'var(--color-chart-seq-7, #2b8cbe)',
  'var(--color-chart-seq-8, #0868ac)',
  'var(--color-chart-seq-9, #084081)',
];

/**
 * Resolve the categorical color for series `index`.
 * Explicit `override` (e.g. per-datum color) always wins.
 */
export function themeDataColor(index: number, override?: string): string {
  if (override) return override;
  return THEME_DATA_PALETTE[index % THEME_DATA_PALETTE.length];
}
