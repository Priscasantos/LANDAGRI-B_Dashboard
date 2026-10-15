import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import AgricultureOverviewPage from '../components/agricultural-analysis/AgricultureOverview/AgricultureOverviewPage';
import CropCalendarPage from '../components/agricultural-analysis/CropCalendar/CropCalendarPage';
import AgricultureAvailabilityPage from '../components/agricultural-analysis/AgricultureAvailability/AgricultureAvailabilityPage';

export default function AgriculturalAnalysisPage() {
  const location = useLocation();

  const subPages = [
    { path: 'overview', label: '🔎 Agriculture Overview' },
    { path: 'crop-calendar', label: '📅 Crop Calendar' },
    { path: 'availability', label: '⏳ Agriculture Availability' },
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
              className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 ${
                isActive ? 'text-amber-700 border-amber-600 font-semibold' : 'text-fg-secondary border-transparent hover:text-fg hover:border-border'
              }`}
            >
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
      </Routes>
    </div>
  );
}
