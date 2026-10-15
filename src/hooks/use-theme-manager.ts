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

/**
 * Escala de raio Tailwind v4 — `rounded-sm/md/lg/xl` resolvem para
 * `--radius-*`, então o customizer precisa gravar a escala inteira, não
 * só `--radius`. Fatores fixos a partir da base (sm −0.25, md −0.125,
 * lg = base, xl +0.25, 2xl +0.5), em rem com 3 casas.
 */
export function radiusScale(base: Radius): Record<string, string> {
  const px: Record<Radius, number> = { sm: 8, md: 12, lg: 16 };
  const b = px[base];
  const toRem = (v: number): string => `${Math.round((v / 16) * 1000) / 1000}rem`;
  return {
    '--radius-sm': toRem(b - 4),
    '--radius-md': toRem(b - 2),
    '--radius-lg': toRem(b),
    '--radius-xl': toRem(b + 4),
    '--radius-2xl': toRem(b + 8),
  };
}

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
  root.dataset.radius = radius;
  root.dataset.font = fontValue;
  root.style.setProperty('--radius', RADIUS_MAP[radius]);
  root.style.setProperty('--card-radius', RADIUS_MAP[radius]);
  for (const [token, value] of Object.entries(radiusScale(radius))) {
    root.style.setProperty(token, value);
  }
  const colors = effective === 'dark' ? preset.dark : preset.light;
  root.style.setProperty('--color-primary', colors.primary);
  root.style.setProperty('--color-primary-hover', colors.primaryHover);
  root.style.setProperty('--color-primary-light', colors.primaryLight);
  root.style.setProperty('--color-accent', colors.accent);
  colors.charts.slice(0, 10).forEach((hex, i) => {
    root.style.setProperty(`--color-chart-${i + 1}`, hex);
  });
  root.style.setProperty('--color-sidebar-bg', colors.sidebarBg);
  root.style.setProperty('--color-sidebar-text', colors.sidebarText);
  root.style.setProperty(
    '--color-sidebar-text-active',
    colors.sidebarTextActive,
  );
  root.style.setProperty('--color-sidebar-active-bg', colors.sidebarActiveBg);
  root.style.setProperty('--color-sidebar-hover-bg', colors.sidebarHoverBg);
  root.style.setProperty('--color-header-overview', colors.headerOverview);
  root.style.setProperty(
    '--color-header-initiative',
    colors.headerInitiative,
  );
  root.style.setProperty(
    '--color-header-agricultural',
    colors.headerAgricultural,
  );
  root.style.setProperty('--color-header-about', colors.headerAbout);
  const font = getFontOption(fontValue);
  root.style.setProperty('--font-sans', font.sans);
  root.style.setProperty('--font-display', font.display);
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
    // Persiste o valor RESOLVIDO (fallback já aplicado pelo getter): um
    // `landagri-preset`/`landagri-font` cru inválido nunca volta ao disco.
    persist(PRESET_KEY, preset.value);
    persist(RADIUS_KEY, radius);
    persist(DENSITY_KEY, density);
    persist(FONT_KEY, getFontOption(fontValue).value);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [presetValue, radius, density, fontValue, effective]);

  /**
   * "Restaurar padrão" = voltar aos defaults do app (preset agro-v2 +
   * confortável + raio md + fonte padrão). NÃO remove as vars inline nem
   * seleciona a opção "Azul": o efeito acima reaplica as vars do preset
   * default, então o resultado visual equivale ao CSS base. (O comentário
   * antigo em `theme-presets.ts` dizia "reset remove as vars" — estava
   * desatualizado; a semântica real é restaurar-defaults via estado.)
   */
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
