import { useMemo, type ReactElement } from 'react';
import { Map, Wheat, MapPin, BarChart3, Sprout } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import conabAvailability from '../../../data/processed/conab_availability.json';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { useT } from '../../../i18n/LanguageContext';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

interface AvailabilityRow {
  'Crop Type;Area;Anos (1S);Anos (2S)': string;
}

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
  if (v === 'P' || v === 'H' || v === 'PH') return 1;
  return 0;
}

/**
 * ECharts pilot of the Availability page (1 route, reversible).
 * Same JSONs, headings and i18n as `AgricultureAvailabilityPage` —
 * only the chart renderer changes (Plotly → ECharts SVG).
 */
export default function AgricultureAvailabilityPage(): ReactElement {
  const { t: tBody } = useT('agricultural');
  const availData = conabAvailability as AvailabilityRow[];
  const calendarData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  // Same parsing as the Plotly original.
  const { stateCoverage, cropDiversity, regionalActivity, activityHeatmap } = useMemo(() => {
    const statesMap: Record<string, StateInfo> = mappingData?.states || {};
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    const cropStates: Record<string, Set<string>> = {};
    const stateYears: Record<string, Set<string>> = {};
    const stateCrops: Record<string, Set<string>> = {};

    for (const row of availData) {
      const entry = row['Crop Type;Area;Anos (1S);Anos (2S)'];
      if (!entry || entry.trim() === '') continue;

      const parts = entry.split(';');
      if (parts.length < 2) continue;

      const crop = parts[0].trim() || 'Unknown';
      const state = parts[1].trim();

      if (!state) continue;

      if (!cropStates[crop]) cropStates[crop] = new Set();
      cropStates[crop].add(state);

      if (!stateCrops[state]) stateCrops[state] = new Set();
      stateCrops[state].add(crop);

      if (parts[2]) {
        if (!stateYears[state]) stateYears[state] = new Set();
        stateYears[state].add(parts[2].trim());
      }
      if (parts[3]) {
        if (!stateYears[state]) stateYears[state] = new Set();
        stateYears[state].add(parts[3].trim());
      }
    }

    const stateCoverageData = Object.entries(stateCrops)
      .map(([state, crops]) => ({
        name: `${state}${stateRegions[state] ? ` (${stateRegions[state]})` : ''}`,
        value: crops.size,
      }))
      .sort((a, b) => b.value - a.value);

    const cropDiversityData = Object.entries(cropStates)
      .map(([crop, states]) => ({ name: crop, value: states.size }))
      .sort((a, b) => b.value - a.value);

    const regionMonthActivity: Record<string, number[]> = {};

    for (const row of calendarData) {
      const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
      if (!entry || entry.trim() === '' || entry.startsWith(';')) continue;

      const parts = entry.split(';');
      if (parts.length < 13) continue;

      const state = parts[1].trim();
      const region = stateRegions[state];
      if (!region) continue;

      if (!regionMonthActivity[region]) {
        regionMonthActivity[region] = MONTHS_SHORT.map(() => 0);
      }

      parts.slice(2).forEach((v, i) => {
        if (parseActivityValue(v) > 0) {
          regionMonthActivity[region][i]++;
        }
      });
    }

    const regionLabels = Object.keys(regionMonthActivity).sort();
    const regionalActivitySeries = regionLabels.map(region => ({
      name: region,
      values: regionMonthActivity[region],
    }));

    const heatmapZ: number[][] = regionLabels.map(r => regionMonthActivity[r]);

    return {
      stateCoverage: {
        labels: stateCoverageData.map(s => s.name),
        values: stateCoverageData.map(s => s.value),
      },
      cropDiversity: {
        labels: cropDiversityData.map(c => c.name),
        values: cropDiversityData.map(c => c.value),
      },
      regionalActivity: {
        categories: MONTHS_SHORT,
        series: regionalActivitySeries,
      },
      activityHeatmap: {
        z: heatmapZ,
        regions: regionLabels,
        months: MONTHS_SHORT,
      },
    };
  }, [availData, calendarData, mappingData]);

  const totalStates = stateCoverage.labels.length;
  const totalCrops = cropDiversity.labels.length;
  const totalRegions = activityHeatmap.regions.length;

  const spatialContent = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <MetricCard icon={Map} label={tBody('metricStatesAvail')} value={totalStates} variant="accuracy" />
        <MetricCard icon={Wheat} label={tBody('metricCropsAvailable')} value={totalCrops} variant="resolution" />
        <MetricCard icon={MapPin} label={tBody('metricRegions')} value={totalRegions} variant="classes" />
      </div>
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSpatialCoverage')}</h3>
        {stateCoverage.values.length > 0 ? (
          <EChartsHorizontalBar
            labels={stateCoverage.labels}
            values={stateCoverage.values}
            captionKey="cropsAvailable"
            color="#EC9706"
            height={Math.max(300, stateCoverage.labels.length * 25)}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noSpatialData')}</p>
        )}
      </Card>
    </div>
  );

  const cropDiversityContent = (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropDiversity')}</h3>
        {cropDiversity.values.length > 0 ? (
          <EChartsHorizontalBar
            labels={cropDiversity.labels}
            values={cropDiversity.values}
            captionKey="statesCount"
            color="#626C01"
            height={Math.max(300, cropDiversity.labels.length * 35)}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noDiversityData')}</p>
        )}
      </Card>
    </div>
  );

  const regionalActivitySubTabs = [
    {
      id: 'comparison',
      label: tBody('subTabComparison'),
      icon: BarChart3,
      content: (
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hRegionalComparison')}</h3>
          {regionalActivity.series.length > 0 ? (
            <EChartsGroupedBar
              categories={regionalActivity.categories}
              series={regionalActivity.series}
              captionKey="activityCount"
              height={400}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noRegionalActivity')}</p>
          )}
        </Card>
      ),
    },
    {
      id: 'heatmap',
      label: tBody('subTabHeatmap'),
      icon: Map,
      content: (
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hRegionalHeatmap')}</h3>
          {activityHeatmap.regions.length > 0 ? (
            <EChartsHeatmap
              z={activityHeatmap.z}
              x={activityHeatmap.months}
              y={activityHeatmap.regions}
              captionKey="activityIntensityByRegionMonth"
              height={Math.max(300, activityHeatmap.regions.length * 60 + 100)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noHeatmapData')}</p>
          )}
        </Card>
      ),
    },
  ];

  const tabs = [
    { id: 'spatial', label: tBody('tabSpatial'), icon: Map, content: spatialContent },
    { id: 'diversity', label: tBody('tabDiversity'), icon: Sprout, content: cropDiversityContent },
    { id: 'regional', label: tBody('tabRegional'), icon: Map, content: <Tabs tabs={regionalActivitySubTabs} /> },
  ];

  return (
    <div>
      <Tabs tabs={tabs} />
    </div>
  );
}
