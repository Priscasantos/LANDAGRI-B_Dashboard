import type { ReactElement } from 'react';
import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  help?: string;
  /** Tooltip (`title`) sobre o valor — ex.: fonte sem OA publicado. */
  valueTitle?: string;
  variant?: 'accuracy' | 'resolution' | 'classes' | 'frequency';
  className?: string;
}

/**
 * shadcn-style MetricCard (Fase 2): `data-slot`, accessible label/value
 * association, decorative icon hidden from AT. Props API unchanged.
 * Superfície canônica (`bg-card`/`border-border`) — sem gradientes
 * saturados; `variant` vira só `data-variant` para testes/estilo.
 * Berry KPI (reversível): avatar 44px rounded-8 tintado + decor
 * `::before`/`::after` warning.dark (`.kpi-decor`) em vez de gradiente.
 */
const AVATAR_TINT: Record<NonNullable<MetricCardProps['variant']>, string> = {
  accuracy: 'bg-amber-500/25 text-amber-700 dark:text-amber-300',
  resolution: 'bg-primary/10 text-primary-hover dark:text-primary',
  classes: 'bg-primary/10 text-primary-hover dark:text-primary',
  frequency: 'bg-primary/10 text-primary-hover dark:text-primary',
};
export default function MetricCard({
  icon: Icon,
  label,
  value,
  help,
  valueTitle,
  variant = 'accuracy',
  className = '',
}: MetricCardProps): ReactElement {
  const labelId = `metric-${variant}-label`;
  const valueId = `metric-${variant}-value`;
  return (
    <div
      data-slot="card"
      data-variant={variant}
      role="group"
      aria-labelledby={labelId}
      aria-describedby={help ? `${valueId}-help` : undefined}
      className={`kpi-decor rounded-lg border border-border bg-card text-card-foreground p-4 flex flex-col items-center min-h-[120px] shadow-sm hover:scale-105 hover:shadow-[0_2px_14px_rgb(32_40_45/8%)] transition-all duration-300 ${className}`}
    >
      <div
        aria-hidden="true"
        className={`mb-1 flex size-11 items-center justify-center rounded-lg ${AVATAR_TINT[variant]}`}
      >
        <Icon size={22} aria-hidden="true" className="shrink-0" />
      </div>
      <div id={labelId} className="text-sm font-semibold text-fg-secondary mb-0.5">
        {label}
      </div>
      <div id={valueId} className="text-2xl font-bold font-display tabular-nums text-fg" title={valueTitle}>
        {value}
      </div>
      {help && (
        <div id={`${valueId}-help`} className="text-xs text-fg-muted mt-1 text-center">
          {help}
        </div>
      )}
    </div>
  );
}
