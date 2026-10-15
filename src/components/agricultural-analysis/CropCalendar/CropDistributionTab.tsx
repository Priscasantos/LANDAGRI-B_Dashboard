import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
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

interface CropDistributionTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function CropDistributionTab({ selectedCrops, selectedRegions }: CropDistributionTabProps) {
  const { t: tBody } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { stateCropCounts, topCropsByStates } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Count how many states each crop appears in
    const cropStates: Record<string, Set<string>> = {};
    // Count how many crops per state
    const stateCrops: Record<string, Set<string>> = {};

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

      if (!cropStates[crop]) cropStates[crop] = new Set();
      cropStates[crop].add(state);

      if (!stateCrops[state]) stateCrops[state] = new Set();
      stateCrops[state].add(crop);
    }

    // Top crops by number of states
    const topCrops = Object.entries(cropStates)
      .map(([crop, states]) => ({ name: crop, count: states.size }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 10);

    // State by crop count (horizontal stacked-like)
    const stateEntries = Object.entries(stateCrops)
      .map(([state, crops]) => ({ name: state, count: crops.size }))
      .sort((a, b) => b.count - a.count);

    // For grouped bar: states x crops
    const topStateEntries = stateEntries.slice(0, 15);
    const cropToStates: Record<string, Record<string, boolean>> = {};
    for (const crop of selectedCrops) {
      cropToStates[crop] = {};
      if (cropStates[crop]) {
        for (const state of cropStates[crop]) {
          cropToStates[crop][state] = true;
        }
      }
    }

    return {
      stateCropCounts: {
        labels: topStateEntries.map(e => e.name),
        values: topStateEntries.map(e => e.count),
      },
      topCropsByStates: {
        labels: topCrops.map(c => c.name),
        values: topCrops.map(c => c.count),
      },
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const noStateData = stateCropCounts.values.every(v => v === 0);

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropDistState')}</h3>
        {noStateData ? (
          <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
        ) : (
          <EChartsHorizontalBar
            labels={stateCropCounts.labels}
            values={stateCropCounts.values}
            captionKey="cropsCount"
            color="#EC9706"
            height={Math.max(300, stateCropCounts.labels.length * 30)}
          />
        )}
      </Card>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hTopCropsStates')}</h3>
        {topCropsByStates.values.length > 0 ? (
          <EChartsHorizontalBar
            labels={topCropsByStates.labels}
            values={topCropsByStates.values}
            captionKey="statesCount"
            color="#626C01"
            height={Math.max(250, topCropsByStates.labels.length * 35)}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
        )}
      </Card>
    </div>
  );
}
