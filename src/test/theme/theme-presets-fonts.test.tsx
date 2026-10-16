import { describe, it, expect, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import {
  THEME_PRESETS,
  DEFAULT_PRESET,
  getThemePreset,
} from '../../config/theme-presets';
import {
  FONT_OPTIONS,
  getFontOption,
  CHART_FONT_FAMILY,
  resolveChartFontFamily,
} from '../../lib/fonts';
import { radiusScale } from '../../hooks/use-theme-manager';
import {
  buildStandardLayout,
  getChartLayout,
} from '../../lib/chartDefaults';
import { ThemeProvider } from '../../components/theme-provider';
import { useThemeManager } from '../../hooks/use-theme-manager';
import * as React from 'react';

function renderManager() {
  return renderHook(() => useThemeManager(), {
    wrapper: ({ children }: { children: React.ReactNode }) => (
      <ThemeProvider>{children}</ThemeProvider>
    ),
  });
}

beforeEach(() => {
  localStorage.clear();
  document.documentElement.classList.remove('dark', 'light');
});

describe('theme presets (agro-v2 default)', () => {
  it('defaults to agro-v2', () => {
    expect(DEFAULT_PRESET).toBe('agro-v2');
    expect(getThemePreset(DEFAULT_PRESET).label).toBe('Verde Agro v2');
  });

  it('exposes Padrão + Verde Agro v2 + Terra + Âmbar', () => {
    const values = THEME_PRESETS.map((p) => p.value);
    expect(values).toEqual(
      expect.arrayContaining(['default', 'agro-v2', 'terra', 'ambar']),
    );
  });

  it('falls back to agro-v2 (not blue Padrão) for unknown values', () => {
    expect(getThemePreset('midnight-neon').value).toBe(DEFAULT_PRESET);
  });
});

describe('fonts (display Sora / body Inter / mono tabular)', () => {
  it('keeps stored option values backward compatible', () => {
    expect(FONT_OPTIONS.map((f) => f.value)).toEqual([
      'default',
      'mono',
      'system',
    ]);
  });

  it('pairs Sora display + Inter body + JetBrains Mono by default', () => {
    const def = getFontOption('default');
    expect(def.sans).toContain('Inter');
    expect(def.display).toContain('Sora');
    expect(def.mono).toContain('JetBrains Mono');
  });

  it('falls back to the default option for unknown values', () => {
    expect(getFontOption('comic-sans').value).toBe('default');
  });

  it('applies --font-sans + --font-display + --font-mono to root in real time', () => {
    renderManager();
    const style = document.documentElement.style;
    expect(style.getPropertyValue('--font-sans')).toContain('Inter');
    expect(style.getPropertyValue('--font-display')).toContain('Sora');
    expect(style.getPropertyValue('--font-mono')).toContain('JetBrains Mono');
  });
});

describe('chartDefaults (theme-aware + shared font stack)', () => {
  it('uses the shared chart font stack (no hardcoded drift)', () => {
    const layout = buildStandardLayout();
    expect(layout.font?.family).toBe(CHART_FONT_FAMILY);
    expect(CHART_FONT_FAMILY).toContain('Inter');
  });

  it('resolves readable dark vs light font colors', () => {
    expect(getChartLayout('dark').font?.color).toBe('#e2e8f0');
    expect(getChartLayout('light').font?.color).toBe('#475569');
  });
});

describe('preset full scope (charts + sidebar + headers por modo)', () => {
  it('every preset ships 10 chart colors + sidebar/header tokens per mode', () => {
    for (const preset of THEME_PRESETS) {
      for (const mode of [preset.light, preset.dark] as const) {
        expect(mode.charts).toHaveLength(10);
        for (const token of [
          mode.primary,
          mode.primaryHover,
          mode.primaryLight,
          mode.accent,
          mode.sidebarBg,
          mode.sidebarText,
          mode.sidebarTextActive,
          mode.sidebarActiveBg,
          mode.sidebarHoverBg,
          mode.headerOverview,
          mode.headerInitiative,
          mode.headerAgricultural,
          mode.headerAbout,
        ] as const) {
          expect(token).not.toBe('');
        }
      }
    }
  });

  it('Terra/Âmbar/Azul differ visibly from agro-v2 (primary + chart-1)', () => {
    const base = getThemePreset('agro-v2');
    for (const value of ['default', 'terra', 'ambar'] as const) {
      const other = getThemePreset(value);
      expect(other.light.primary).not.toBe(base.light.primary);
      expect(other.light.charts[0]).not.toBe(base.light.charts[0]);
    }
  });

  it('applyToRoot writes primary-light + charts + sidebar + headers + radius scale', () => {
    const { result } = renderManager();
    act(() => {
      result.current.setPreset('terra');
    });
    const style = document.documentElement.style;
    expect(style.getPropertyValue('--color-primary-light')).not.toBe('');
    expect(style.getPropertyValue('--color-chart-1')).not.toBe('');
    expect(style.getPropertyValue('--color-chart-10')).not.toBe('');
    expect(style.getPropertyValue('--color-sidebar-active-bg')).not.toBe('');
    expect(style.getPropertyValue('--color-header-overview')).toContain(
      'gradient',
    );
    expect(style.getPropertyValue('--radius-sm')).not.toBe('');
    expect(style.getPropertyValue('--radius-2xl')).not.toBe('');
    expect(document.documentElement.dataset.preset).toBe('terra');
  });

  it('persists the resolved preset/font (invalid raw values never hit storage)', () => {
    localStorage.setItem('landagri-preset', 'midnight-neon');
    localStorage.setItem('landagri-font', 'comic-sans');
    renderManager();
    expect(localStorage.getItem('landagri-preset')).toBe(DEFAULT_PRESET);
    expect(localStorage.getItem('landagri-font')).toBe('default');
  });

  it('radiusScale derives the Tailwind v4 --radius-* scale from the base', () => {
    expect(radiusScale('md')).toMatchObject({
      '--radius-sm': '0.5rem',
      '--radius-md': '0.625rem',
      '--radius-lg': '0.75rem',
      '--radius-xl': '1rem',
      '--radius-2xl': '1.25rem',
    });
  });
});

describe('resolveChartFontFamily (fonte do customizer nos gráficos)', () => {
  it('resolves Mono/Sistema stacks (Plotly precisa de string concreta)', () => {
    expect(resolveChartFontFamily('mono')).toContain('JetBrains Mono');
    expect(resolveChartFontFamily('system')).toContain('system-ui');
    expect(resolveChartFontFamily('default')).toContain('Inter');
  });

  it('reads the live data-font from root when no value is passed', () => {
    document.documentElement.dataset.font = 'mono';
    expect(buildStandardLayout().font?.family).toContain('JetBrains Mono');
    expect(getChartLayout('light').font?.family).toContain('JetBrains Mono');
  });

  it('honours an explicit override without touching the DOM', () => {
    document.documentElement.dataset.font = 'default';
    const layout = buildStandardLayout({}, 'system-ui, sans-serif');
    expect(layout.font?.family).toBe('system-ui, sans-serif');
  });
});
