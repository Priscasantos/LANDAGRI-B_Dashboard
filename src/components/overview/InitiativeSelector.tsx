import { useDashboardStore } from '../../stores/dashboardStore';
import Select from '../ui/Select';
import { useT } from '../../i18n/LanguageContext';

export default function InitiativeSelector() {
  const { t } = useT('overview');
  const { initiatives, selection, setSelectedInitiative } = useDashboardStore();

  const options = initiatives.map((i) => ({
    value: i.Name,
    label: `${i.Name} (${i.Acronym})`,
  }));

  return (
    <Select
      label={t('selectLabel')}
      options={options}
      value={selection.selectedInitiative || ''}
      onChange={(val) => setSelectedInitiative(val)}
      placeholder={t('selectPlaceholder')}
    />
  );
}
