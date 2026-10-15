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
 */
export default function Breadcrumb({ segments }: BreadcrumbProps): React.JSX.Element | null {
  if (segments.length === 0) return null;
  return (
    <nav aria-label="breadcrumb">
      <ol className="flex min-w-0 flex-wrap items-center gap-1.5 text-sm text-fg-secondary">
        {segments.map((segment, index) => {
          const isLast = index === segments.length - 1;
          return (
            <li key={`${segment.label}-${index}`} className="flex min-w-0 items-center gap-1.5">
              {index > 0 && (
                <span aria-hidden="true" className="text-fg-muted">
                  /
                </span>
              )}
              {isLast || !segment.to ? (
                <span aria-current="page" className="truncate font-medium text-fg">
                  {segment.label}
                </span>
              ) : (
                <Link
                  to={segment.to}
                  className="truncate transition-colors hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
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

