import Tabs from '../../ui/Tabs';
import { Map, Leaf } from 'lucide-react';
import ConabMappingTab from './ConabMappingTab';
import ConabEstimatesTab from './ConabEstimatesTab';
import IbgeEstimatesTab from './IbgeEstimatesTab';

export default function AgricultureOverviewPage() {
  const tabs = [
    { id: 'conab-mapping', label: 'CONAB Mapping', icon: Map, content: <ConabMappingTab /> },
    { id: 'conab-estimates', label: 'CONAB Estimates', icon: Leaf, content: <ConabEstimatesTab /> },
    { id: 'ibge-estimates', label: 'IBGE Estimates', icon: Leaf, content: <IbgeEstimatesTab /> },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
