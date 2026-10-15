import Tabs from '../../ui/Tabs';
import { GitCompare, LineChart, Target, Calculator, Tags, Microscope, Flame, ClipboardList } from 'lucide-react';
import { useT } from '../../../i18n/LanguageContext';
import PairwiseTab from './PairwiseTab';
import DistributionsTab from './DistributionsTab';
import GlobalAccuracyTab from './GlobalAccuracyTab';
import MethodologyDistributionTab from './MethodologyDistributionTab';
import ClassDetailsTab from './ClassDetailsTab';
import MethodologyDeepDiveTab from './MethodologyDeepDiveTab';
import NormalizedPerformanceTab from './NormalizedPerformanceTab';
import DetailedTableTab from './DetailedTableTab';

export default function ComparativePage() {
  const { t } = useT('initiative');
  const tabs = [
    { id: 'pairwise', label: t('tabPairwise'), icon: GitCompare, content: <PairwiseTab /> },
    { id: 'distributions', label: t('tabDistributions'), icon: LineChart, content: <DistributionsTab /> },
    { id: 'accuracy', label: t('tabGlobalAccuracy'), icon: Target, content: <GlobalAccuracyTab /> },
    { id: 'methodology', label: t('tabMethodologyDist'), icon: Calculator, content: <MethodologyDistributionTab /> },
    { id: 'classes', label: t('tabClassDetails'), icon: Tags, content: <ClassDetailsTab /> },
    { id: 'deepdive', label: t('tabDeepDive'), icon: Microscope, content: <MethodologyDeepDiveTab /> },
    { id: 'normalized', label: t('tabNormalized'), icon: Flame, content: <NormalizedPerformanceTab /> },
    { id: 'table', label: t('tabDetailedTable'), icon: ClipboardList, content: <DetailedTableTab /> },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
