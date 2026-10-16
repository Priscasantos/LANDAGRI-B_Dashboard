import type { ReactElement } from 'react';
import { useT } from '../../../i18n/LanguageContext';
import type { Recency } from '../../../lib/calendarShare';

interface RecencyBadgeProps {
  recency: Recency | null;
}

/**
 * Badge de recência da fonte (Fase 2): fonte/safra/atualizado em.
 * `null` → nada (sem inventar proveniência).
 */
export default function RecencyBadge({ recency }: RecencyBadgeProps): ReactElement | null {
  const { t } = useT('agricultural');
  if (recency === null) return null;
  return (
    <p
      className="text-xs text-fg-secondary"
      role="note"
      aria-label={t('recencyLabel', {
        source: recency.source,
        vintage: recency.vintage,
        date: recency.updatedAt,
      })}
    >
      {t('recencyLabel', {
        source: recency.source,
        vintage: recency.vintage,
        date: recency.updatedAt,
      })}
    </p>
  );
}
