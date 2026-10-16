import { useState } from 'react';
import { GitCompare, LineChart, Target, Calculator, Tags, Microscope, Flame, ClipboardList, Columns2 } from 'lucide-react';
import { useT } from '../../../i18n/LanguageContext';
import ViewSwitcher from '../../ui/ViewSwitcher';
import PairwiseTab from './PairwiseTab';
import DistributionsTab from './DistributionsTab';
import GlobalAccuracyTab from './GlobalAccuracyTab';
import MethodologyDistributionTab from './MethodologyDistributionTab';
import ClassDetailsTab from './ClassDetailsTab';
import MethodologyDeepDiveTab from './MethodologyDeepDiveTab';
import NormalizedPerformanceTab from './NormalizedPerformanceTab';
import DetailedTableTab from './DetailedTableTab';
import SplitCompareTab from './SplitCompareTab';

export default function ComparativePage(): React.JSX.Element {
  const { t } = useT('initiative');
  const { t: tNav } = useT('nav');
  const [view, setView] = useState<string>('pairwise');

  const options = [
    { id: 'pairwise', label: t('tabPairwise'), icon: GitCompare },
    { id: 'split', label: t('tabSplit'), icon: Columns2 },
    { id: 'distributions', label: t('tabDistributions'), icon: LineChart },
    { id: 'accuracy', label: t('tabGlobalAccuracy'), icon: Target },
    { id: 'methodology', label: t('tabMethodologyDist'), icon: Calculator },
    { id: 'classes', label: t('tabClassDetails'), icon: Tags },
    { id: 'deepdive', label: t('tabDeepDive'), icon: Microscope },
    { id: 'normalized', label: t('tabNormalized'), icon: Flame },
    { id: 'table', label: t('tabDetailedTable'), icon: ClipboardList },
  ];
  const bodies: Record<string, React.JSX.Element> = {
    pairwise: <PairwiseTab />,
    split: <SplitCompareTab />,
    distributions: <DistributionsTab />,
    accuracy: <GlobalAccuracyTab />,
    methodology: <MethodologyDistributionTab />,
    classes: <ClassDetailsTab />,
    deepdive: <MethodologyDeepDiveTab />,
    normalized: <NormalizedPerformanceTab />,
    table: <DetailedTableTab />,
  };

  return (
    <div>
      {/* Fase 3: tabs internas viram ToggleGroup (desktop) + Select (mobile), mesmo estado */}
      <ViewSwitcher label={tNav('comparative')} options={options} value={view} onChange={setView} />
      <div>{bodies[view] ?? bodies.pairwise}</div>
    </div>
  );
}
