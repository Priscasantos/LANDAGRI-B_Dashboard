import Tabs from '../../ui/Tabs';
import { GitCompare, LineChart, Target, Calculator, Tags, Microscope, Flame, ClipboardList } from 'lucide-react';
import PairwiseTab from './PairwiseTab';
import DistributionsTab from './DistributionsTab';
import GlobalAccuracyTab from './GlobalAccuracyTab';
import MethodologyDistributionTab from './MethodologyDistributionTab';
import ClassDetailsTab from './ClassDetailsTab';
import MethodologyDeepDiveTab from './MethodologyDeepDiveTab';
import NormalizedPerformanceTab from './NormalizedPerformanceTab';
import DetailedTableTab from './DetailedTableTab';

export default function ComparativePage() {
  const tabs = [
    { id: 'pairwise', label: 'a/b Pairwise Performance', icon: GitCompare, content: <PairwiseTab /> },
    { id: 'distributions', label: 'Distributions Analysis', icon: LineChart, content: <DistributionsTab /> },
    { id: 'accuracy', label: 'Global Accuracy', icon: Target, content: <GlobalAccuracyTab /> },
    { id: 'methodology', label: 'Methodology Distribution', icon: Calculator, content: <MethodologyDistributionTab /> },
    { id: 'classes', label: 'Class Details', icon: Tags, content: <ClassDetailsTab /> },
    { id: 'deepdive', label: 'Methodology Deep Dive', icon: Microscope, content: <MethodologyDeepDiveTab /> },
    { id: 'normalized', label: 'Normalized Performance', icon: Flame, content: <NormalizedPerformanceTab /> },
    { id: 'table', label: 'Detailed Table', icon: ClipboardList, content: <DetailedTableTab /> },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
