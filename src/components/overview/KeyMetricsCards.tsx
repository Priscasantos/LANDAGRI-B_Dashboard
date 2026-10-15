import type { InitiativeRow } from '../../types/initiative';
import MetricCard from '../ui/MetricCard';
import { Target, Satellite, Tags, CalendarDays } from 'lucide-react';
import { parseAvailableYears } from '../../lib/dataParser';
import { useT } from '../../i18n/LanguageContext';

interface KeyMetricsCardsProps {
  data: InitiativeRow;
}


export default function KeyMetricsCards({ data }: KeyMetricsCardsProps) {
  const { t } = useT('overview');
  const years = parseAvailableYears(data.Available_Years);
  const yearsCoverage = years.length;

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <MetricCard
        icon={Target}
        label={t('kmAccuracy')}
        value={data.Accuracy > 0 ? `${data.Accuracy.toFixed(1)}%` : '-'}
        help={t('kmAccuracyHelp')}
        variant="accuracy"
      />
      <MetricCard
        icon={Satellite}
        label={t('kmResolution')}
        value={data.Resolution > 0 ? `${data.Resolution.toFixed(0)}m` : '-'}
        help={t('kmResolutionHelp')}
        variant="resolution"
      />
      <MetricCard
        icon={Tags}
        label={t('kmClasses')}
        value={data.Number_of_Classes > 0 ? String(data.Number_of_Classes) : '-'}
        help={t('kmClassesHelp')}
        variant="classes"
      />
      <MetricCard
        icon={CalendarDays}
        label={t('kmTemporal')}
        value={yearsCoverage > 0 ? String(yearsCoverage) : '-'}
        help={t('kmTemporalHelp')}
        variant="frequency"
      />
    </div>
  );
}
