import { useMemo } from 'react';
import { GanttChart, TrendingUp, Clock, TriangleAlert } from 'lucide-react';
import { useDashboardStore } from '../../../stores/dashboardStore';
import Tabs from '../../ui/Tabs';
import { useT } from '../../../i18n/LanguageContext';
import TimelineTab from './TimelineTab';
import EvolutionTab from './EvolutionTab';
import CoverageTab from './CoverageTab';
import GapAnalysisTab from './GapAnalysisTab';

export default function TemporalPage() {
  const { t } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const temporalData = useMemo(
    () =>
      initiatives
        .filter((i) => i.Available_Years.length > 0)
        .map((i) => ({
          name: i.Name,
          displayName: i.Display_Name,
          firstYear: i.Year_Start,
          lastYear: i.Year_End,
          years: i.Available_Years,
          coverageYears: i.Available_Years.length,
          totalPeriod: i.Year_End - i.Year_Start + 1,
          coveragePct:
            i.Year_End > i.Year_Start
              ? Math.round((i.Available_Years.length / (i.Year_End - i.Year_Start + 1)) * 100 * 10) / 10
              : 0,
          methodology: i.Methodology,
          coverage: i.Coverage,
        })),
    [initiatives],
  );

  const tabs = [
    {
      id: 'timeline',
      label: t('tabTimeline'),
      icon: GanttChart,
      content: <TimelineTab data={temporalData} />,
    },
    {
      id: 'evolution',
      label: t('tabEvolution'),
      icon: TrendingUp,
      content: <EvolutionTab data={temporalData} />,
    },
    {
      id: 'coverage',
      label: t('tabTemporalCoverage'),
      icon: Clock,
      content: <CoverageTab data={temporalData} />,
    },
    {
      id: 'gaps',
      label: t('tabGapAnalysis'),
      icon: TriangleAlert,
      content: <GapAnalysisTab data={temporalData} />,
    },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
