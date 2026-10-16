import { Link } from 'react-router-dom';

export interface BreadcrumbSegment {
  label: string;
  to?: string;
}

interface BreadcrumbProps {
  segments: BreadcrumbSegment[];
}

/**
 * Accessible breadcrumb (adapted from the shadcn-dashboard reference).
 * Plain semantic markup — no extra dependencies. Hidden from the
 * accessibility tree when there is nothing to trail beyond the home.
 * Fase 3 IA enxuta: no máximo 2 níveis (corta o meio) + ellipsis no
 * mobile (trunca com `max-w`, expande em `sm+`).
 */
export default function Breadcrumb({ segments }: BreadcrumbProps): React.JSX.Element | null {
  if (segments.length === 0) return null;
  const visible = segments.length > 2 ? [segments[0], segments[segments.length - 1]] : segments;
  return (
    <nav aria-label="breadcrumb" className="min-w-0">
      <ol className="flex min-w-0 flex-wrap items-center gap-1.5 text-sm text-fg-secondary">
        {visible.map((segment, index) => {
          const isLast = index === visible.length - 1;
          return (
            <li key={`${segment.label}-${index}`} className="flex min-w-0 items-center gap-1.5">
              {index > 0 && (
                <span aria-hidden="true" className="shrink-0 text-fg-muted">
                  /
                </span>
              )}
              {isLast || !segment.to ? (
                <span aria-current="page" className="truncate font-medium text-fg max-w-[38vw] sm:max-w-none">
                  {segment.label}
                </span>
              ) : (
                <Link
                  to={segment.to}
                  className="truncate max-w-[28vw] sm:max-w-none transition-colors hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
                >
                  {segment.label}
                </Link>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
