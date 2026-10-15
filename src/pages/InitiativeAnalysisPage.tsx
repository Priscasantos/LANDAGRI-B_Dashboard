import { Routes, Route, Navigate, useLocation, Link } from 'react-router-dom';
import TemporalPage from '../components/initiative-analysis/TemporalAnalysis/TemporalPage';
import ComparativePage from '../components/initiative-analysis/ComparativeAnalysis/ComparativePage';
import DetailedPage from '../components/initiative-analysis/DetailedAnalysis/DetailedPage';
import { MODULE_THEMES } from '../types/theme';

export default function InitiativeAnalysisPage() {
  const location = useLocation();
  const moduleTheme = MODULE_THEMES['Initiative Analysis'];

  const subPages = [
    { path: 'temporal', label: '⏳ Temporal Analysis' },
    { path: 'comparative', label: '🔠 Comparative Analysis' },
    { path: 'detailed', label: '◌ Detailed Analysis' },
  ];

  return (
    <div>
      <p className="mt-2 text-base md:text-lg italic text-center text-fg-secondary">
        Reference: {' '}
        <a href="https://doi.org/10.3390/rs17132324" target="_blank" rel="noopener noreferrer" style={{ color: moduleTheme.primary, textDecoration: 'underline', fontWeight: 600 }}>
          Santos et al. (2025).
        </a>
      </p>

      {/* Sub-page navigation tabs */}
      <div className="flex border-b border-border mb-6 overflow-x-auto">
        {subPages.map((tab) => {
          const isActive = location.pathname.includes(tab.path);
          return (
            <Link
              key={tab.path}
              to={`/initiative-analysis/${tab.path}`}
              className={`px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-all duration-200 ${
                isActive ? '' : 'text-fg-secondary'
              }`}
              style={{
                borderColor: isActive ? moduleTheme.primary : 'transparent',
                color: isActive ? moduleTheme.primary : undefined,
              }}
            >
              {tab.label}
            </Link>
          );
        })}
      </div>

      <Routes>
        <Route index element={<Navigate to="temporal" replace />} />
        <Route path="temporal" element={<TemporalPage />} />
        <Route path="comparative" element={<ComparativePage />} />
        <Route path="detailed" element={<DetailedPage />} />
      </Routes>
    </div>
  );
}
