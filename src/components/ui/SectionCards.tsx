import type { ComponentType, ReactElement, ReactNode } from 'react';
import Card from './Card';
import { useT } from '../../i18n/LanguageContext';

export interface SectionCardItem {
  /** Stable key for the grid cell. */
  key: string;
  /** Small uppercase label (e.g. "Avg Accuracy"). */
  label: string;
  /** Main value (e.g. "92.5%" or "12"). */
  value: string;
  /** Optional sub-line (e.g. "42% of total"). */
  hint?: string;
  /** Optional decorative icon; hidden from assistive tech. */
  Icon?: ComponentType<{ size?: number | string; className?: string; 'aria-hidden'?: boolean | 'true' | 'false' }>;
}

interface SectionCardsProps {
  /** Overview = coverage distribution + perf metrics; initiative = detail metrics. */
  variant: 'overview' | 'initiative';
  /** Accessible list name (also used as section label). */
  title: string;
  items: SectionCardItem[];
  className?: string;
  /**
   * Render decorative icon wrappers with `aria-hidden` (default true).
   * Kept as a prop so tests can assert the accessible contract.
   */
  iconAriaHidden?: boolean;
}

/**
 * SectionCards — Fase 2 successor of SummaryCards.
 * Generic responsive card grid (`role="list"`) for the Overview and
 * Initiative sections. Content (agro metrics) unchanged; layout only.
 */
export default function SectionCards({
  variant,
  title,
  items,
  className = '',
  iconAriaHidden = true,
}: SectionCardsProps): ReactElement {
  const { t } = useT('common');
  if (items.length === 0) {
    return (
      <p className="text-sm text-fg-muted py-4 text-center" role="status">
        {t('noDataFor', { title })}
      </p>
    );
  }

  return (
    <div
      className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}
      role="list"
      aria-label={title}
      data-variant={variant}
    >
      {items.map(({ key, label, value, hint, Icon }) => (
        <Card key={key} padding="sm" title={`${label}: ${value}`}>
          <div className="text-center" role="listitem">
            {Icon ? (
              <span aria-hidden={iconAriaHidden ? 'true' : undefined}>
                <Icon size={24} aria-hidden="true" className="mx-auto mb-1 text-fg-secondary" />
              </span>
            ) : null}
            <div className="text-xs font-medium text-fg-secondary uppercase tracking-wider">{label}</div>
            <div className="text-2xl font-bold text-fg mt-1">{value}</div>
            {hint ? <div className="text-xs text-fg-muted mt-0.5">{hint}</div> : null}
          </div>
        </Card>
      ))}
    </div>
  );
}

export type { ReactNode };
