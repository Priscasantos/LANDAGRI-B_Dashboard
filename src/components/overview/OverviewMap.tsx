import { lazy, Suspense, type ReactElement } from 'react';
import DashboardSkeleton from '../ui/DashboardSkeleton';
import { useT } from '../../i18n/LanguageContext';

/** Lazy boundary: leaflet stays out of the main chunk (island). */
const LazyLeafletMap = lazy(() => import('./LeafletMapInner'));

/**
 * OverviewMap — Fase 2 leaflet island for the Overview route.
 * Rendered inside route-level `Suspense`; shows a skeleton while the
 * `leaflet` chunk loads. Reversible: remove the usage in `OverviewPage`.
 */
export default function OverviewMap(): ReactElement {
  const { t } = useT('map');
  return (
    <section aria-labelledby="overview-map-heading" className="mt-8">
      <h2 id="overview-map-heading" className="text-xl font-bold text-fg mb-4">
        {t('title')}
      </h2>
      <Suspense
        fallback={
          <div role="status" aria-label={t('loading')}>
            <DashboardSkeleton />
          </div>
        }
      >
        <LazyLeafletMap />
      </Suspense>
    </section>
  );
}
