import { Link } from 'react-router-dom';
import type { LucideIcon } from 'lucide-react';

export interface FilterOption {
  value: string;
  label: string;
  /** Deep-link canônico — idêntico ao `to=` das tabs antigas (contrato preservado). */
  to: string;
  icon?: LucideIcon;
}

interface FilterBarProps {
  /** Rótulo acessível da barra (`role="toolbar"`). */
  label: string;
  options: FilterOption[];
  /** Valor ativo (derivado da rota — sem estado interno). */
  value: string;
}

/**
 * Fase 3 IA enxuta: substitui as tabs-link de `AgriculturalAnalysisPage`
 * por uma barra de filtros route-backed. Mesmos `to=` (deep-link
 * preservado), filtro ativo anunciado via `aria-current="page"`.
 */
export default function FilterBar({ label, options, value }: FilterBarProps): React.JSX.Element {
  return (
    <div
      role="toolbar"
      aria-label={label}
      className="mb-6 snap-x snap-mandatory overflow-x-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      <ul className="flex items-center gap-2 py-0.5">
        {options.map((option) => {
          const isActive = option.value === value;
          const Icon = option.icon;
          return (
            <li key={option.value} className="shrink-0 snap-start">
              <Link
                to={option.to}
                aria-current={isActive ? 'page' : undefined}
                aria-pressed={isActive}
                className={`inline-flex min-h-[44px] items-center gap-1.5 rounded-full border px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary ${
                  isActive
                    ? 'border-primary bg-primary font-semibold text-white'
                    : 'border-border bg-surface text-fg-secondary hover:border-fg-muted hover:text-fg'
                }`}
              >
                {Icon ? <Icon size={15} aria-hidden="true" className="shrink-0" /> : null}
                <span className="truncate">{option.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
