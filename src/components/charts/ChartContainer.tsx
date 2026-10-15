import type { ReactElement, ReactNode } from 'react';
import Card from '../ui/Card';

interface ChartContainerProps {
  /** Chart title — rendered as heading + figure label. */
  title: string;
  /** Optional source/method note (e.g. "Fonte: IBGE PAM/PPM e CONAB"). */
  description?: string;
  children: ReactNode;
  className?: string;
}

/**
 * ChartContainer — Fase 2 chart shell (shadcn-style).
 * Wraps the existing recharts wrappers with a titled `Card`; colors come
 * from the `theme-data` palette (CSS vars), never hardcoded hex here.
 * Reversible: pure layout wrapper, no chart logic.
 */
export default function ChartContainer({
  title,
  description,
  children,
  className = '',
}: ChartContainerProps): ReactElement {
  const headingId = `chart-${title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`;
  return (
    <Card
      title={title}
      titleAsHeading={false}
      className={`focus-within:ring-2 focus-within:ring-blue-500 ${className}`}
    >
      <section aria-labelledby={headingId}>
        <h3 id={headingId} className="text-base font-semibold text-fg mb-1">
          {title}
        </h3>
        {description ? <p className="text-xs text-fg-muted mb-3">{description}</p> : null}
        {children}
      </section>
    </Card>
  );
}
