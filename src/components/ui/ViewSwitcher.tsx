import { useId } from 'react';
import { ChevronDown } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';

export interface ViewOption {
  id: string;
  label: string;
  icon?: LucideIcon;
}

interface ViewSwitcherProps {
  /** Rótulo acessível compartilhado (radiogroup desktop + select mobile). */
  label: string;
  options: ViewOption[];
  value: string;
  onChange: (id: string) => void;
}

/**
 * Fase 3 IA enxuta: substitui as `Tabs` internas de `ComparativePage`.
 * Desktop: ToggleGroup (`radiogroup` com roving tabindex + setas).
 * Mobile: `<select>` nativo. Ambos dirigem o mesmo estado — sem rotas,
 * sem deep-link (comportamento interno preservado).
 */
export default function ViewSwitcher({ label, options, value, onChange }: ViewSwitcherProps): React.JSX.Element {
  const selectId = useId();
  const activeIndex = Math.max(
    0,
    options.findIndex((option) => option.id === value),
  );

  function move(delta: number): void {
    const next = options[(activeIndex + delta + options.length) % options.length];
    if (next) onChange(next.id);
  }

  function handleRadioKeyDown(event: React.KeyboardEvent<HTMLDivElement>): void {
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
      event.preventDefault();
      move(1);
    } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
      event.preventDefault();
      move(-1);
    } else if (event.key === 'Home') {
      event.preventDefault();
      const first = options[0];
      if (first) onChange(first.id);
    } else if (event.key === 'End') {
      event.preventDefault();
      const last = options[options.length - 1];
      if (last) onChange(last.id);
    }
  }

  return (
    <div className="mb-4">
      {/* Desktop/tablet: ToggleGroup */}
      <div
        role="radiogroup"
        aria-label={label}
        onKeyDown={handleRadioKeyDown}
        className="mb-4 hidden gap-1 overflow-x-auto border-b border-border sm:flex"
      >
        {options.map((option, index) => {
          const isActive = option.id === value;
          const Icon = option.icon;
          return (
            <button
              key={option.id}
              type="button"
              role="radio"
              aria-checked={isActive}
              tabIndex={index === activeIndex ? 0 : -1}
              onClick={() => onChange(option.id)}
              className="inline-flex min-h-[44px] shrink-0 items-center gap-1.5 border-b-2 -mb-px px-4 py-2.5 text-sm whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
              style={{
                borderBottomColor: isActive ? 'var(--color-primary)' : 'transparent',
                color: isActive ? 'var(--color-primary)' : 'var(--color-fg-muted)',
                fontWeight: isActive ? 600 : 400,
              }}
            >
              {Icon ? <Icon size={15} aria-hidden="true" className="shrink-0" /> : null}
              {option.label}
            </button>
          );
        })}
      </div>
      {/* Mobile: Select nativo */}
      <div className="mb-4 sm:hidden">
        <label htmlFor={selectId} className="sr-only">
          {label}
        </label>
        <div className="relative">
          <select
            id={selectId}
            aria-label={label}
            value={value}
            onChange={(event) => onChange(event.target.value)}
            className="min-h-[44px] w-full appearance-none rounded-lg border border-border bg-surface py-2.5 pr-10 pl-3 text-sm text-fg shadow-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            {options.map((option) => (
              <option key={option.id} value={option.id}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown
            size={16}
            aria-hidden="true"
            className="pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-fg-muted"
          />
        </div>
      </div>
    </div>
  );
}
