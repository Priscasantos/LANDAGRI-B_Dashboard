/**
 * Font options — puro stack CSS, sem dependência pesada (Fase 3).
 * Aplicado via `--font-sans`/`--font-mono` na raiz + `data-font`.
 */
export interface FontOption {
  value: string;
  label: string;
  sans: string;
  mono: string;
}

const SYSTEM_SANS =
  '"Inter", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif';
const SYSTEM_MONO = '"JetBrains Mono", "Fira Code", ui-monospace, monospace';

export const FONT_OPTIONS: readonly FontOption[] = [
  {
    value: 'default',
    label: 'Padrão',
    sans: SYSTEM_SANS,
    mono: SYSTEM_MONO,
  },
  {
    value: 'mono',
    label: 'Mono (dados)',
    sans: SYSTEM_MONO,
    mono: SYSTEM_MONO,
  },
  {
    value: 'system',
    label: 'Sistema',
    sans: 'system-ui, -apple-system, "Segoe UI", Roboto, sans-serif',
    mono: 'ui-monospace, SFMono-Regular, Menlo, monospace',
  },
];

export function getFontOption(value: string): FontOption {
  return FONT_OPTIONS.find((f) => f.value === value) ?? FONT_OPTIONS[0];
}
