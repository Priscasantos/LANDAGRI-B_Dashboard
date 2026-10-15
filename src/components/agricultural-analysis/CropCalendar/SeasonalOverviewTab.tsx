import { useMemo } from 'react';
import Card from '../../ui/Card';
import GroupedBarChart from '../../charts/GroupedBarChart';
import { useT } from '../../../i18n/LanguageContext';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';

interface CalendarRow {
  'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September': string;
}

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
}

interface SeasonalOverviewTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function SeasonalOverviewTab({ selectedCrops, selectedRegions }: SeasonalOverviewTabProps) {
  const { t } = useT('charts');
  const { t: tBody } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const seasonalData = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Seasonal month groups
    const seasons = {
      'Spring (Oct-Dec)': [0, 1, 2],
      'Summer (Jan-Mar)': [3, 4, 5],
      'Autumn (Apr-Jun)': [6, 7, 8],
      'Winter (Jul-Sep)': [9, 10, 11],
    };

    const seasonNames = Object.keys(seasons);
    const plantBySeason: Record<string, number> = {};
    const harvestBySeason: Record<string, number> = {};

    for (const name of seasonNames) {
      plantBySeason[name] = 0;
      harvestBySeason[name] = 0;
    }

    for (const row of rawData) {
      const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
      if (!entry || entry.trim() === '' || entry.startsWith(';')) continue;

      const parts = entry.split(';');
      if (parts.length < 13) continue;

      const crop = parts[0].trim();
      if (!crop || !selectedCrops.includes(crop)) continue;

      const state = parts[1].trim();
      const region = stateRegions[state];
      if (region && !selectedRegions.includes(region)) continue;

      parts.slice(2).forEach((v, i) => {
        const val = v?.trim() || '';
        for (const [seasonName, months] of Object.entries(seasons)) {
          if (months.includes(i)) {
            if (val === 'P' || val === 'PH') plantBySeason[seasonName]++;
            if (val === 'H' || val === 'PH') harvestBySeason[seasonName]++;
          }
        }
      });
    }

    return {
      categories: seasonNames,
      series: [
        { name: 'Planting', values: seasonNames.map(s => plantBySeason[s]) },
        { name: 'Harvest', values: seasonNames.map(s => harvestBySeason[s]) },
      ],
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const noData = seasonalData.series.every(s => s.values.every(v => v === 0));

  return (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSeasonal')}</h3>
      {noData ? (
        <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
      ) : (
        <GroupedBarChart
          categories={seasonalData.categories}
          series={seasonalData.series}
          xlabel={t('season')}
          ylabel={t('activityCount')}
          height={400}
        />
      )}
      <div className="mt-4 p-3 bg-surface-alt rounded-lg">
        <p className="text-xs text-fg-secondary">
          <strong>{tBody('noteLabel')}</strong> {tBody('seasonNote')}
        </p>
      </div>
    </Card>
  );
}
