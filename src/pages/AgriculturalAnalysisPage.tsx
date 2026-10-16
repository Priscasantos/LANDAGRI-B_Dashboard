import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Sprout, CalendarDays, Package } from 'lucide-react';
import { useT } from '../i18n/LanguageContext';
import FilterBar from '../components/ui/FilterBar';
import AgricultureOverviewPage from '../components/agricultural-analysis/AgricultureOverview/AgricultureOverviewPage';
import CropCalendarPage from '../components/agricultural-analysis/CropCalendar/CropCalendarPage';
import AgricultureAvailabilityPage from '../components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityPage';


export default function AgriculturalAnalysisPage(): React.JSX.Element {
  const { t } = useT('nav');
  const location = useLocation();

  const options = [
    { value: 'overview', label: t('agriOverview'), to: '/agricultural-analysis/overview', icon: Sprout },
    { value: 'crop-calendar', label: t('cropCalendar'), to: '/agricultural-analysis/crop-calendar', icon: CalendarDays },
    { value: 'availability', label: t('availability'), to: '/agricultural-analysis/availability', icon: Package },
  ];
  const active = options.find((opt) => location.pathname.endsWith(`/${opt.value}`))?.value ?? 'overview';

  return (
    <div>
      {/* Fase 3: sub-navegação como barra de filtros route-backed (mesmos `to=`, deep-link preservado) */}
      <FilterBar label={t('agriculturalAnalysis')} options={options} value={active} />
      <Routes>
        <Route index element={<Navigate to="overview" replace />} />
        <Route path="overview" element={<AgricultureOverviewPage />} />
        <Route path="crop-calendar" element={<CropCalendarPage />} />
        <Route path="availability" element={<AgricultureAvailabilityPage />} />
      </Routes>
    </div>
  );
}
