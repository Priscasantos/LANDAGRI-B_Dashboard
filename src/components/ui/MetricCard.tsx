import type { ReactElement } from 'react';

interface MetricCardProps {
  icon: string;
  label: string;
  value: string | number;
  help?: string;
  variant?: 'accuracy' | 'resolution' | 'classes' | 'frequency';
  className?: string;
}

/**
 * shadcn-style MetricCard (Fase 2): `data-slot`, accessible label/value
 * association, decorative icon hidden from AT. Props API unchanged.
 */
export default function MetricCard({
  icon,
  label,
  value,
  help,
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
      className={`rounded-xl p-4 flex flex-col items-center min-h-[120px] shadow-sm hover:scale-105 transition-all duration-300 ${className}`}
      style={{
        background: `var(--gradient-${variant})`,
      }}
    >
      <div className="text-3xl mb-1" aria-hidden="true">
        {icon}
      </div>
      <div id={labelId} className="text-sm font-semibold text-fg-secondary mb-0.5">
        {label}
      </div>
      <div id={valueId} className="text-2xl font-bold text-fg">
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
