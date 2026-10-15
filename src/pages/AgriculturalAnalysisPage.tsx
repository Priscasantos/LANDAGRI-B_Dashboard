import { Suspense, lazy } from 'react';
import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import { Sprout, CalendarDays, Package } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { useT } from '../i18n/LanguageContext';
import AgricultureOverviewPage from '../components/agricultural-analysis/AgricultureOverview/AgricultureOverviewPage';
import CropCalendarPage from '../components/agricultural-analysis/CropCalendar/CropCalendarPage';
import AgricultureAvailabilityPage from '../components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityPage';

// ECharts pilot (reversible): lazy so the echarts chunk loads only on this route.
const AgricultureAvailabilityEChartsPilotPage = lazy(
  () => import('../components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityEChartsPilotPage'),
);


export default function AgriculturalAnalysisPage() {
  const { t } = useT('nav');
  const location = useLocation();

  const subPages: { path: string; label: string; icon: LucideIcon }[] = [
    { path: 'overview', label: t('agriOverview'), icon: Sprout },
    { path: 'crop-calendar', label: t('cropCalendar'), icon: CalendarDays },
    { path: 'availability', label: t('availability'), icon: Package },
  ];

  return (
    <div>
      <div className="flex border-b border-border mb-6 overflow-x-auto">
        {subPages.map((tab) => {
          const isActive = location.pathname.includes(tab.path);
          return (
            <Link
              key={tab.path}
              to={`/agricultural-analysis/${tab.path}`}
              className={`inline-flex items-center gap-1.5 px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 ${
                isActive ? 'text-amber-700 border-amber-600 font-semibold' : 'text-fg-secondary border-transparent hover:text-fg hover:border-border'
              }`}
            >
              <tab.icon size={15} aria-hidden="true" className="shrink-0" />
              {tab.label}
            </Link>
          );
        })}
      </div>
      <Routes>
        <Route index element={<Navigate to="overview" replace />} />
        <Route path="overview" element={<AgricultureOverviewPage />} />
        <Route path="crop-calendar" element={<CropCalendarPage />} />
        <Route path="availability" element={<AgricultureAvailabilityPage />} />
        <Route
          path="availability-echarts"
          element={
            <Suspense fallback={null}>
              <AgricultureAvailabilityEChartsPilotPage />
            </Suspense>
          }
        />
      </Routes>
    </div>
  );
}
