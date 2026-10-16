import { Link } from 'react-router-dom';
import type { LucideIcon } from 'lucide-react';

export interface SegmentedOption {
  value: string;
  label: string;
  /** Deep-link canônico — idêntico ao `to=` das tabs antigas (contrato preservado). */
  to: string;
  icon?: LucideIcon;
}

interface SegmentedControlProps {
  /** Rótulo acessível do grupo (`<nav aria-label>`). */
  label: string;
  options: SegmentedOption[];
  /** Valor ativo (derivado da rota — sem estado interno). */
  value: string;
}

/**
 * Fase 3 IA enxuta: substitui as tabs-link de `InitiativeAnalysisPage`
 * por um segmented control route-backed. Mesmos `to=` (deep-link
 * preservado), ativo anunciado via `aria-current="page"`.
 */
export default function SegmentedControl({ label, options, value }: SegmentedControlProps): React.JSX.Element {
  return (
    <nav
      aria-label={label}
      className="mb-6 snap-x snap-mandatory overflow-x-auto [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden"
    >
      <ul className="inline-flex min-w-full items-center gap-1 rounded-xl border border-border bg-surface-alt p-1 sm:w-auto">
        {options.map((option) => {
          const isActive = option.value === value;
          const Icon = option.icon;
          return (
            <li key={option.value} className="min-w-0 flex-1 snap-start sm:flex-none">
              <Link
                to={option.to}
                aria-current={isActive ? 'page' : undefined}
                className={`flex min-h-[44px] w-full items-center justify-center gap-1.5 rounded-lg border px-4 py-2 text-sm font-medium whitespace-nowrap transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:justify-start ${
                  isActive
                    ? 'border-transparent bg-surface font-semibold text-fg shadow-sm'
                    : 'border-transparent text-fg-secondary hover:text-fg'
                }`}
              >
                {Icon ? <Icon size={15} aria-hidden="true" className="shrink-0" /> : null}
                <span className="truncate">{option.label}</span>
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
