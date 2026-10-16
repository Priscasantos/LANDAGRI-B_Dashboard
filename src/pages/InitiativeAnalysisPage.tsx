import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Clock, GitCompare, FileSearch } from 'lucide-react';
import TemporalPage from '../components/initiative-analysis/TemporalAnalysis/TemporalPage';
import ComparativePage from '../components/initiative-analysis/ComparativeAnalysis/ComparativePage';
import DetailedPage from '../components/initiative-analysis/DetailedAnalysis/DetailedPage';
import SegmentedControl from '../components/ui/SegmentedControl';
import { MODULE_THEMES } from '../types/theme';
import { useT } from '../i18n/LanguageContext';

export default function InitiativeAnalysisPage(): React.JSX.Element {
  const { t } = useT('nav');
  const { t: tBody } = useT('initiative');
  const location = useLocation();
  const moduleTheme = MODULE_THEMES['Initiative Analysis'];

  const options = [
    { value: 'temporal', label: t('temporal'), to: '/initiative-analysis/temporal', icon: Clock },
    { value: 'comparative', label: t('comparative'), to: '/initiative-analysis/comparative', icon: GitCompare },
    { value: 'detailed', label: t('detailed'), to: '/initiative-analysis/detailed', icon: FileSearch },
  ];
  const active = options.find((opt) => location.pathname.endsWith(`/${opt.value}`))?.value ?? 'temporal';

  return (
    <div>
      <p className="mt-2 text-base md:text-lg italic text-center text-fg-secondary">
        {tBody('reference')}: {' '}
        <a href="https://doi.org/10.3390/rs17132324" target="_blank" rel="noopener noreferrer" style={{ color: moduleTheme.primary, textDecoration: 'underline', fontWeight: 600 }}>
          Santos et al. (2025).
        </a>
      </p>

      {/* Fase 3: sub-navegação como segmented control route-backed (mesmos `to=`, deep-link preservado) */}
      <div className="mt-4">
        <SegmentedControl label={t('initiativeAnalysis')} options={options} value={active} />
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
