import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsLine from '../../charts/echarts/EChartsLine';
import { useT } from '../../../i18n/LanguageContext';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';

const MONTHS_FULL = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];
const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

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

function parseActivityValue(val: string): number {
  if (!val || val.trim() === '') return 0;
  const v = val.trim();
  if (v === 'PH') return 2;
  if (v === 'P' || v === 'H') return 1;
  return 0;
}

interface MonthlyIntensityTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function MonthlyIntensityTab({ selectedCrops, selectedRegions }: MonthlyIntensityTabProps) {
  const { t: tBody } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { heatmapZ, intensitySeries } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Per-crop per-month intensity
    const cropMonthIntensity: Record<string, number[]> = {};
    const totalIntensity: number[] = MONTHS_FULL.map(() => 0);

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

      if (!cropMonthIntensity[crop]) {
        cropMonthIntensity[crop] = MONTHS_FULL.map(() => 0);
      }

      parts.slice(2).forEach((v, i) => {
        const intensity = parseActivityValue(v);
        cropMonthIntensity[crop][i] += intensity;
        totalIntensity[i] += intensity;
      });
    }

    // Build heatmap Z: rows = crops, cols = months
    const cropLabels: string[] = [];
    const z: number[][] = [];

    for (const [crop, intensities] of Object.entries(cropMonthIntensity)) {
      if (selectedCrops.includes(crop)) {
        cropLabels.push(crop);
        z.push(intensities);
      }
    }

    return {
      heatmapZ: { z, crops: cropLabels, months: MONTHS_SHORT },
      intensitySeries: {
        series: [{
          name: 'Activity Intensity',
          x: MONTHS_SHORT,
          y: totalIntensity,
          color: '#EC9706',
        }],
      },
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const noData = intensitySeries.series[0].y.every(v => v === 0);

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hMonthlyHeatmap')}</h3>
        {noData ? (
          <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
        ) : (
          <EChartsHeatmap
            z={heatmapZ.z}
            x={heatmapZ.months}
            y={heatmapZ.crops}
            captionKey="activityIntensityCropsMonths"
            height={Math.max(300, heatmapZ.crops.length * 40 + 100)}
            colors={['#f3f4f6', '#fef3c7', '#f97316', '#dc2626']}
          />
        )}
      </Card>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hIntensityByMonth')}</h3>
        {noData ? (
          <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
        ) : (
          <EChartsLine
            series={intensitySeries.series}
            captionKey="totalActivityCount"
            height={350}
          />
        )}
      </Card>
    </div>
  );
}
