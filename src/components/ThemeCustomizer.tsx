import { useEffect, useState, type ReactElement } from 'react';
import { SlidersHorizontal } from 'lucide-react';

type Density = 'comfortable' | 'compact';
type Radius = 'sm' | 'md' | 'lg';

const DENSITY_KEY = 'landagri-density';
const RADIUS_KEY = 'landagri-radius';

const RADIUS_MAP: Record<Radius, string> = {
  sm: '0.5rem',
  md: '0.75rem',
  lg: '1rem',
};

const DENSITY_OPTIONS: { value: Density; label: string }[] = [
  { value: 'comfortable', label: 'Confortável' },
  { value: 'compact', label: 'Compacta' },
];

const RADIUS_OPTIONS: { value: Radius; label: string }[] = [
  { value: 'sm', label: 'Pequeno' },
  { value: 'md', label: 'Médio' },
  { value: 'lg', label: 'Grande' },
];

function readStored<T extends string>(key: string, fallback: T, allowed: readonly T[]): T {
  try {
    const stored = localStorage.getItem(key);
    if (stored && (allowed as readonly string[]).includes(stored)) return stored as T;
  } catch {
    /* jsdom/SSR sem localStorage — usa fallback */
  }
  return fallback;
}

function applyToRoot(density: Density, radius: Radius): void {
  const root = document.documentElement;
  root.dataset.density = density;
  root.style.setProperty('--card-radius', RADIUS_MAP[radius]);
}

/**
 * ThemeCustomizer leve — somente densidade + raio (Fase 2).
 * Sem radix/cmdk/novas deps: usa <button> + radios nativos, persiste em
 * localStorage e aplica via `data-density` + `--card-radius`. Reversível.
 */
export default function ThemeCustomizer(): ReactElement {
  const [open, setOpen] = useState(false);
  const [density, setDensity] = useState<Density>(() =>
    readStored(DENSITY_KEY, 'comfortable', ['comfortable', 'compact'] as const),
  );
  const [radius, setRadius] = useState<Radius>(() =>
    readStored(RADIUS_KEY, 'md', ['sm', 'md', 'lg'] as const),
  );

  useEffect(() => {
    applyToRoot(density, radius);
    try {
      localStorage.setItem(DENSITY_KEY, density);
      localStorage.setItem(RADIUS_KEY, radius);
    } catch {
      /* armazenamento indisponível — mantém só em memória */
    }
  }, [density, radius]);

  const radioClass =
    'flex items-center gap-2 rounded-lg border border-border px-3 py-1.5 text-xs cursor-pointer focus-within:ring-2 focus-within:ring-blue-500';

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        aria-label="Personalizar densidade e raio"
        title="Personalizar densidade e raio"
        className="flex items-center justify-center w-9 h-9 rounded-lg bg-transparent hover:bg-surface-hover text-fg-secondary transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <SlidersHorizontal size={18} aria-hidden="true" />
      </button>
      {open && (
        <div
          role="dialog"
          aria-label="Personalizar densidade e raio"
          className="absolute right-0 mt-2 w-64 rounded-xl border border-border bg-surface p-4 shadow-lg z-50 space-y-4"
        >
          <fieldset>
            <legend className="text-xs font-bold uppercase tracking-wider text-fg-muted mb-2">
              Densidade
            </legend>
            <div className="flex gap-2">
              {DENSITY_OPTIONS.map((d) => (
                <label key={d.value} className={radioClass}>
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
            <div className="flex gap-2">
              {RADIUS_OPTIONS.map((r) => (
                <label key={r.value} className={radioClass}>
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
        </div>
      )}
    </div>
  );
}
