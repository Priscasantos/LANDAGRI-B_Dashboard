import type { ReactNode, ReactElement } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  padding?: 'sm' | 'md' | 'lg';
  hover?: boolean;
  /** Accessible title — rendered as heading when `titleAsHeading` is set, else `aria-label`. */
  title?: string;
  titleAsHeading?: boolean;
}

const paddingMap = { sm: 'p-4', md: 'p-5', lg: 'p-6' } as const;

/**
 * shadcn-style Card (Fase 2): `data-slot` attributes, theme tokens,
 * keyboard focus ring. Props API unchanged (reversible).
 */
export default function Card({
  children,
  className = '',
  padding = 'md',
  hover = true,
  title,
  titleAsHeading = false,
}: CardProps): ReactElement {
  return (
    <div
      data-slot="card"
      aria-label={title && !titleAsHeading ? title : undefined}
      className={`rounded-xl border bg-surface border-border shadow-sm ${hover ? 'hover:-translate-y-0.5 hover:shadow-lg' : ''}
        ${paddingMap[padding]}
        transition-all duration-300 focus-within:ring-2 focus-within:ring-blue-500 ${className}`}
    >
      {title && titleAsHeading ? (
        <h3 data-slot="card-title" className="text-base font-medium text-fg mb-3">
          {title}
        </h3>
      ) : null}
      <div data-slot="card-content">{children}</div>
    </div>
  );
}
