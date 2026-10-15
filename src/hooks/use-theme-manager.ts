import * as React from 'react';
import { useEffectiveTheme } from './use-theme';
import {
  getThemePreset,
  DEFAULT_PRESET,
  type ThemePreset,
} from '../config/theme-presets';
import { getFontOption } from '../lib/fonts';

export type Density = 'comfortable' | 'compact';
export type Radius = 'sm' | 'md' | 'lg';

export const DENSITY_KEY = 'landagri-density';
export const RADIUS_KEY = 'landagri-radius';
export const PRESET_KEY = 'landagri-preset';
export const FONT_KEY = 'landagri-font';

export const DENSITY_OPTIONS: readonly { value: Density; label: string }[] = [
  { value: 'comfortable', label: 'Confortável' },
  { value: 'compact', label: 'Compacta' },
];

export const RADIUS_OPTIONS: readonly { value: Radius; label: string }[] = [
  { value: 'sm', label: 'Pequeno' },
  { value: 'md', label: 'Médio' },
  { value: 'lg', label: 'Grande' },
];

export const RADIUS_MAP: Record<Radius, string> = {
  sm: '0.5rem',
  md: '0.75rem',
  lg: '1rem',
};

function readStored<T extends string>(
  key: string,
  fallback: T,
  allowed: readonly T[],
): T {
  try {
    const stored = localStorage.getItem(key);
    if (stored && (allowed as readonly string[]).includes(stored)) {
      return stored as T;
    }
  } catch {
    /* jsdom/SSR sem localStorage — usa fallback */
  }
  return fallback;
}

function persist(key: string, value: string): void {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* armazenamento indisponível — mantém só em memória */
  }
}

function applyToRoot(
  preset: ThemePreset,
  radius: Radius,
  density: Density,
  fontValue: string,
  effective: 'light' | 'dark',
): void {
  const root = document.documentElement;
  root.dataset.density = density;
  root.dataset.preset = preset.value;
  root.dataset.font = fontValue;
  root.style.setProperty('--radius', RADIUS_MAP[radius]);
  root.style.setProperty('--card-radius', RADIUS_MAP[radius]);
  const colors = effective === 'dark' ? preset.dark : preset.light;
  root.style.setProperty('--color-primary', colors.primary);
  root.style.setProperty('--color-primary-hover', colors.primaryHover);
  root.style.setProperty('--color-accent', colors.accent);
  const font = getFontOption(fontValue);
  root.style.setProperty('--font-sans', font.sans);
  root.style.setProperty('--font-mono', font.mono);
}

/**
 * Manager leve do customizer (Fase 3) — preset + raio + densidade + fonte.
 * Sem radix/cmdk/novas deps: estado + CSS vars + localStorage. Reversível
 * via `resetCustomizations()`.
 */
export function useThemeManager() {
  const effective = useEffectiveTheme();
  const [presetValue, setPresetValue] = React.useState<string>(() =>
    readStored(
      PRESET_KEY,
      DEFAULT_PRESET,
      ['default', 'agro', 'agro-v2', 'terra', 'ambar'] as const,
    ),
  );
  const [radius, setRadius] = React.useState<Radius>(() =>
    readStored(RADIUS_KEY, 'md', ['sm', 'md', 'lg'] as const),
  );
  const [density, setDensityState] = React.useState<Density>(() =>
    readStored(DENSITY_KEY, 'comfortable', ['comfortable', 'compact'] as const),
  );
  const [fontValue, setFontValue] = React.useState<string>(() =>
    readStored(FONT_KEY, 'default', ['default', 'mono', 'system'] as const),
  );

  const preset = getThemePreset(presetValue);

  React.useEffect(() => {
    applyToRoot(preset, radius, density, fontValue, effective);
    persist(PRESET_KEY, presetValue);
    persist(RADIUS_KEY, radius);
    persist(DENSITY_KEY, density);
    persist(FONT_KEY, fontValue);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [presetValue, radius, density, fontValue, effective]);

  const resetCustomizations = React.useCallback((): void => {
    setPresetValue(DEFAULT_PRESET);
    setRadius('md');
    setDensityState('comfortable');
    setFontValue('default');
  }, []);

  return {
    preset,
    setPreset: setPresetValue,
    radius,
    setRadius,
    density,
    setDensity: setDensityState,
    font: fontValue,
    setFont: setFontValue,
    resetCustomizations,
  };
}
