import { useState, type ReactElement } from 'react';
import { SlidersHorizontal } from 'lucide-react';
import {
  useThemeManager,
  DENSITY_OPTIONS,
  RADIUS_OPTIONS,
} from '../hooks/use-theme-manager';
import { THEME_PRESETS } from '../config/theme-presets';
import { FONT_OPTIONS } from '../lib/fonts';

const RADIO_CARD_CLASS =
  'flex min-w-0 max-w-full items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-xs cursor-pointer focus-within:ring-2 focus-within:ring-blue-500';

/**
 * ThemeCustomizer completo (Fase 3) — predefinição + densidade + raio + fonte.
 * Adaptado do `theme-customizer` da referência, sem Sheet/Tabs/radix/cmdk:
 * popover nativo + radios nativos, persiste em localStorage via
 * `useThemeManager` e aplica via CSS vars + `data-*` na raiz. Reversível.
 */
export default function ThemeCustomizer(): ReactElement {
  const [open, setOpen] = useState(false);
  const {
    preset,
    setPreset,
    radius,
    setRadius,
    density,
    setDensity,
    font,
    setFont,
    resetCustomizations,
  } = useThemeManager();

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Personalizar tema"
        title="Personalizar tema"
        className="flex items-center justify-center w-9 h-9 rounded-lg bg-transparent hover:bg-surface-hover text-fg-secondary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <SlidersHorizontal size={18} aria-hidden="true" />
      </button>
      {open && (
        <div
          role="dialog"
          aria-label="Personalizar tema"
          className="absolute right-0 mr-2 mt-2 w-72 max-w-[calc(100vw-1rem)] rounded-xl border border-border bg-surface p-4 shadow-lg z-50 space-y-4"
        >
          <fieldset>
            <legend className="text-xs font-bold uppercase tracking-wider text-fg-muted mb-2">
              Predefinição
            </legend>
            <div className="grid grid-cols-2 gap-2">
              {THEME_PRESETS.map((p) => (
                <label key={p.value} className={RADIO_CARD_CLASS}>
                  <input
                    type="radio"
                    name="landagri-preset"
                    aria-label={p.label}
                    checked={preset.value === p.value}
                    onChange={() => setPreset(p.value)}
                    className="accent-blue-500"
                  />
                  <span
                    aria-hidden="true"
                    className="inline-block size-3 rounded-full border border-border"
                    style={{ backgroundColor: p.light.primary }}
                  />
                  <span aria-hidden="true" className="text-xs font-medium text-fg">
                    {p.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="text-xs font-bold uppercase tracking-wider text-fg-muted mb-2">
              Densidade
            </legend>
            <div className="flex flex-wrap gap-2">
              {DENSITY_OPTIONS.map((d) => (
                <label key={d.value} className={RADIO_CARD_CLASS}>
                  <input
                    type="radio"
                    name="landagri-density"
                    aria-label={d.label}
                    checked={density === d.value}
                    onChange={() => setDensity(d.value)}
                    className="accent-blue-500"
                  />
                  <span aria-hidden="true" className="text-xs font-medium text-fg">
                    {d.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="text-xs font-bold uppercase tracking-wider text-fg-muted mb-2">
              Raio das bordas
            </legend>
            <div className="flex flex-wrap gap-2">
              {RADIUS_OPTIONS.map((r) => (
                <label key={r.value} className={RADIO_CARD_CLASS}>
                  <input
                    type="radio"
                    name="landagri-radius"
                    aria-label={r.label}
                    checked={radius === r.value}
                    onChange={() => setRadius(r.value)}
                    className="accent-blue-500"
                  />
                  <span aria-hidden="true" className="text-xs font-medium text-fg">
                    {r.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <fieldset>
            <legend className="text-xs font-bold uppercase tracking-wider text-fg-muted mb-2">
              Fonte
            </legend>
            <div className="flex flex-col gap-2">
              {FONT_OPTIONS.map((f) => (
                <label key={f.value} className={RADIO_CARD_CLASS}>
                  <input
                    type="radio"
                    name="landagri-font"
                    aria-label={f.label}
                    checked={font === f.value}
                    onChange={() => setFont(f.value)}
                    className="accent-blue-500"
                  />
                  <span aria-hidden="true" className="text-xs font-medium text-fg">
                    {f.label}
                  </span>
                </label>
              ))}
            </div>
          </fieldset>
          <button
            type="button"
            onClick={resetCustomizations}
            className="w-full rounded-lg border border-border px-3 py-1.5 text-xs font-medium text-fg-secondary hover:bg-surface-hover focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            Restaurar padrão
          </button>
        </div>
      )}
    </div>
  );
}
