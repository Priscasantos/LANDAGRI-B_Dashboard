/**
 * Presets leves de cor (Fase 3) — alternativa sem peso aos ~40 presets
 * oklch da referência (`shadcn-ui-theme-presets`).
 *
 * Cada preset define `primary`/`accent` hex para light+dark; o manager
 * aplica como CSS vars (`--color-primary`, `--color-accent`) na raiz.
 * Reversível: `reset` remove as vars e volta aos tokens do `index.css`.
 */
export interface ThemePresetColors {
  primary: string;
  primaryHover: string;
  accent: string;
}

export interface ThemePreset {
  value: string;
  label: string;
  light: ThemePresetColors;
  dark: ThemePresetColors;
}

export const THEME_PRESETS: readonly ThemePreset[] = [
  {
    value: 'default',
    label: 'Padrão',
    light: { primary: '#3b82f6', primaryHover: '#2563eb', accent: '#eff6ff' },
    dark: { primary: '#60a5fa', primaryHover: '#3b82f6', accent: '#1e3a5f' },
  },
  {
    value: 'agro',
    label: 'Verde Agro',
    light: { primary: '#626C01', primaryHover: '#4d5601', accent: '#f7fee7' },
    dark: { primary: '#a3b018', primaryHover: '#626C01', accent: '#1a2e05' },
  },
  {
    value: 'terra',
    label: 'Terra',
    light: { primary: '#80400B', primaryHover: '#653208', accent: '#fef3c7' },
    dark: { primary: '#d08a3e', primaryHover: '#80400B', accent: '#451a03' },
  },
  {
    value: 'ambar',
    label: 'Âmbar',
    light: { primary: '#EC9706', primaryHover: '#c67d05', accent: '#ffedd5' },
    dark: { primary: '#fbbf24', primaryHover: '#EC9706', accent: '#451a03' },
  },
];

export const DEFAULT_PRESET = 'default';

export function getThemePreset(value: string): ThemePreset {
  return THEME_PRESETS.find((p) => p.value === value) ?? THEME_PRESETS[0];
}
