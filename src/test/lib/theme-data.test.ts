import { describe, it, expect } from 'vitest';
import {
  THEME_DATA_PALETTE,
  THEME_DATA_DIVERGING,
  THEME_DATA_SEQUENTIAL,
  themeDataColor,
} from '../../lib/theme-data';

describe('theme-data (Fase 2: single palette source)', () => {
  it('exposes a non-empty categorical palette', () => {
    expect(THEME_DATA_PALETTE.length).toBeGreaterThanOrEqual(10);
  });

  it('palette entries are theme tokens (CSS vars), not bare hex', () => {
    for (const entry of THEME_DATA_PALETTE) {
      expect(entry.startsWith('var(--color-chart-')).toBe(true);
    }
  });

  it('themeDataColor cycles and honors override', () => {
    expect(themeDataColor(0)).toBe(THEME_DATA_PALETTE[0]);
    expect(themeDataColor(THEME_DATA_PALETTE.length)).toBe(THEME_DATA_PALETTE[0]);
    expect(themeDataColor(3, '#ff0000')).toBe('#ff0000');
  });

  it('exposes diverging + sequential scales', () => {
    expect(THEME_DATA_DIVERGING.length).toBeGreaterThan(0);
    expect(THEME_DATA_SEQUENTIAL.length).toBeGreaterThan(0);
  });
});
