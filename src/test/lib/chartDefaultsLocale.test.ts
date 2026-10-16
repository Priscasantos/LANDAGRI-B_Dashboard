import { describe, expect, it, beforeEach } from 'vitest';
import {
  HOVER_TEMPLATES,
  buildStandardLayout,
  getChartLayout,
  hoverTemplatesForLocale,
  separatorsForLocale,
} from '../../lib/chartDefaults';

describe('chartDefaults locale (Fase 1 i18n)', () => {
  beforeEach(() => {
    document.documentElement.lang = 'pt-BR';
  });

  it('resolves separators per locale (pt-BR decimal vírgula)', () => {
    expect(separatorsForLocale('pt-BR')).toBe(',.');
    expect(separatorsForLocale('en')).toBe('.,');
  });

  it('exposes hover templates per language (default PT)', () => {
    expect(HOVER_TEMPLATES.default).toContain('Valor');
    expect(hoverTemplatesForLocale('pt-BR').default).toContain('Valor');
    expect(hoverTemplatesForLocale('pt-BR').timeline).toContain('Período');
    expect(hoverTemplatesForLocale('en').default).toContain('Value');
    expect(hoverTemplatesForLocale('en').timeline).toContain('Period');
  });

  it('buildStandardLayout applies the active-locale separators', () => {
    document.documentElement.lang = 'pt-BR';
    expect(buildStandardLayout().separators).toBe(',.');
    document.documentElement.lang = 'en';
    expect(buildStandardLayout().separators).toBe('.,');
  });

  it('getChartLayout carries separators without changing the palette', () => {
    document.documentElement.lang = 'en';
    const layout = getChartLayout('light');
    expect(layout.separators).toBe('.,');
    expect(layout.colorway?.[0]).toBe('#2E7D32');
  });
});

describe('chartDefaults theme chrome (Fase 2 qualidade)', () => {
  beforeEach(() => {
    document.documentElement.lang = 'pt-BR';
  });

  it('resolves the title font color per theme (AA on canvas)', () => {
    const light = getChartLayout('light');
    const dark = getChartLayout('dark');
    const lightColor = (
      light.title as { font?: { color?: string } } | undefined
    )?.font?.color;
    const darkColor = (dark.title as { font?: { color?: string } } | undefined)
      ?.font?.color;
    expect(lightColor).toBe('#1e293b');
    expect(darkColor).toBe('#e2e8f0');
  });

  it('keeps the bottom legend geometry in the theme layout (y -0.28)', () => {
    for (const theme of ['light', 'dark'] as const) {
      const legend = getChartLayout(theme).legend as
        | { orientation?: string; y?: number; x?: number }
        | undefined;
      expect(legend?.orientation).toBe('h');
      expect(legend?.y).toBe(-0.28);
      expect(legend?.x).toBe(0.5);
    }
  });

  it('uses a theme-aware legend background (dark Berry surface)', () => {
    const light = getChartLayout('light').legend as
      | { bgcolor?: string }
      | undefined;
    const dark = getChartLayout('dark').legend as
      | { bgcolor?: string }
      | undefined;
    expect(light?.bgcolor).toBe('#ffffff');
    expect(dark?.bgcolor).toBe('rgba(30,41,59,0.9)');
  });
});
