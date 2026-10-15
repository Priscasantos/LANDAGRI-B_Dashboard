import { useMemo } from 'react';
import DataTable from '../../ui/DataTable';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { translateMethodology } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

export default function DetailedTableTab() {
  const { t, locale } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const tableData = useMemo(
    () =>
      initiatives.map((i) => ({
        name: i.Display_Name,
        acronym: i.Acronym,
        provider: i.Provider,
        coverage: i.Coverage,
        methodology: translateMethodology(i.Methodology, locale),
        accuracy: i.Accuracy > 0 ? `${i.Accuracy.toFixed(1)}%` : '-',
        resolution: i.Resolution > 0 ? `${i.Resolution}m` : '-',
        classes: i.Number_of_Classes,
        agriClasses: i.Number_of_Agriculture_Classes,
        years: i.Available_Years.length,
        period: `${i.Year_Start}–${i.Year_End}`,
        frequency: i.Temporal_Frequency,
      })),
    [initiatives, locale],
  );

  const columns = [
    { key: 'name', label: t('colInitiative') },
    { key: 'acronym', label: t('colAcronym') },
    { key: 'provider', label: t('colProvider') },
    { key: 'coverage', label: t('colCoverage') },
    { key: 'methodology', label: t('colMethodology') },
    { key: 'accuracy', label: t('colAccuracy') },
    { key: 'resolution', label: t('colResolution') },
    { key: 'classes', label: t('colClasses') },
    { key: 'agriClasses', label: t('colAgriClasses') },
    { key: 'years', label: t('colYears') },
    { key: 'period', label: t('colPeriod') },
    { key: 'frequency', label: t('colFrequency') },
  ];

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {t('tableIntro')}
      </p>
      <DataTable columns={columns} data={tableData} className="max-h-[600px] overflow-y-auto" />
    </div>
  );
}
