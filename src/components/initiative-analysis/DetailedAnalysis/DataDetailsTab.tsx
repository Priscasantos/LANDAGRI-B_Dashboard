import { useMemo } from 'react';
import DataTable from '../../ui/DataTable';
import { useDashboardStore } from '../../../stores/dashboardStore';
import { translateMethodology } from '../../../data/glossary';
import { useT } from '../../../i18n/LanguageContext';

interface DataDetailsTabProps {
  selectedInitiatives: string[];
}

export default function DataDetailsTab({ selectedInitiatives }: DataDetailsTabProps) {
  const { t, locale } = useT('initiative');
  const initiatives = useDashboardStore((s) => s.initiatives);

  const tableData = useMemo(
    () =>
      initiatives
        .filter((i) => selectedInitiatives.includes(i.Name))
        .map((i) => ({
          displayName: i.Display_Name,
          acronym: i.Acronym,
          provider: i.Provider,
          source: i.Source,
          coverage: i.Coverage,
          methodology: translateMethodology(i.Methodology, locale),
          accuracy: i.Accuracy > 0 ? i.Accuracy.toFixed(1) : '-',
          accuracyMin: i.Accuracy_Min > 0 ? i.Accuracy_Min.toFixed(1) : '-',
          accuracyMax: i.Accuracy_Max > 0 ? i.Accuracy_Max.toFixed(1) : '-',
          resolution: i.Resolution > 0 ? `${i.Resolution}` : '-',
          resolutionMin: i.Resolution_Min > 0 ? `${i.Resolution_Min}` : '-',
          resolutionMax: i.Resolution_Max > 0 ? `${i.Resolution_Max}` : '-',
          classes: String(i.Number_of_Classes),
          agriClasses: String(i.Number_of_Agriculture_Classes),
          agriCapabilities: i.Agricultural_Capabilities || '-',
          startYear: String(i.Year_Start),
          endYear: String(i.Year_End),
          years: String(i.Available_Years.length),
          frequency: i.Temporal_Frequency,
          algorithm: translateMethodology(i.Algorithm, locale),
          classificationMethod: translateMethodology(i.Classification_Method, locale),
        })),
    [initiatives, selectedInitiatives, locale],
  );

  const columns = [
    { key: 'displayName', label: t('colInitiative') },
    { key: 'acronym', label: t('colAcronym') },
    { key: 'provider', label: t('colProvider') },
    { key: 'source', label: t('colSource') },
    { key: 'coverage', label: t('colCoverage') },
    { key: 'methodology', label: t('colMethodology') },
    { key: 'accuracy', label: t('colAccuracyPct') },
    { key: 'accuracyMin', label: t('colAccMin') },
    { key: 'accuracyMax', label: t('colAccMax') },
    { key: 'resolution', label: t('colResolutionM') },
    { key: 'resolutionMin', label: t('colResMin') },
    { key: 'resolutionMax', label: t('colResMax') },
    { key: 'classes', label: t('colClasses') },
    { key: 'agriClasses', label: t('colAgriClasses') },
    { key: 'agriCapabilities', label: t('colAgriCapabilities') },
    { key: 'startYear', label: t('colStartYear') },
    { key: 'endYear', label: t('colEndYear') },
    { key: 'years', label: t('colYearsData') },
    { key: 'frequency', label: t('colFrequency') },
    { key: 'algorithm', label: t('colAlgorithm') },
    { key: 'classificationMethod', label: t('colClassMethod') },
  ];

  if (tableData.length === 0) {
    return (
      <div className="py-8 text-center text-fg-muted">
        {t('noSelectionMulti')}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <p className="text-sm text-fg-secondary">
        {t('dataDetailsIntro')}
      </p>
      <DataTable columns={columns} data={tableData} className="max-h-[600px] overflow-y-auto" />
    </div>
  );
}
