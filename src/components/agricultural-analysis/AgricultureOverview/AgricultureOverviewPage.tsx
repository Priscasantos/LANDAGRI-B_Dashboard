import Tabs from '../../ui/Tabs';
import { useT } from '../../../i18n/LanguageContext';
import { Map, Leaf } from 'lucide-react';
import ConabMappingTab from './ConabMappingTab';
import ConabEstimatesTab from './ConabEstimatesTab';
import IbgeEstimatesTab from './IbgeEstimatesTab';

export default function AgricultureOverviewPage() {
  const { t } = useT('agricultural');
  const tabs = [
    { id: 'conab-mapping', label: t('tabConabMapping'), icon: Map, content: <ConabMappingTab /> },
    { id: 'conab-estimates', label: t('tabConabEstimates'), icon: Leaf, content: <ConabEstimatesTab /> },
    { id: 'ibge-estimates', label: t('tabIbgeEstimates'), icon: Leaf, content: <IbgeEstimatesTab /> },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
