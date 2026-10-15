import { useMemo } from 'react';
import { BarChart3, Zap, Map, TrendingUp } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateActivity,
  translateMonthShort,
  translateRegion,
} from '../../../data/glossary';
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

interface ActivityIntensityTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function ActivityIntensityTab({ selectedCrops, selectedRegions }: ActivityIntensityTabProps) {
  const { t: tBody, locale } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { intensityMatrix, peakActivity, densityByRegion, concentrationIndex } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // State × Month intensity
    const stateMonthIntensity: Record<string, number[]> = {};
    const regionMonthIntensity: Record<string, number[]> = {};
    const stateCropCount: Record<string, Set<string>> = {};

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

      if (!stateMonthIntensity[state]) {
        stateMonthIntensity[state] = MONTHS_FULL.map(() => 0);
      }
      if (!stateCropCount[state]) stateCropCount[state] = new Set();
      stateCropCount[state].add(crop);

      if (region && !regionMonthIntensity[region]) {
        regionMonthIntensity[region] = MONTHS_FULL.map(() => 0);
      }

      parts.slice(2).forEach((v, i) => {
        const intensity = parseActivityValue(v);
        stateMonthIntensity[state][i] += intensity;
        if (region) regionMonthIntensity[region][i] += intensity;
      });
    }

    // Intensity matrix: states × months
    const stateLabels = Object.keys(stateMonthIntensity).sort();
    const z: number[][] = stateLabels.map(s => stateMonthIntensity[s]);

    // Peak activity: max intensity month per state
    const peakMonths = stateLabels.map(state => {
      const intensities = stateMonthIntensity[state];
      const maxVal = Math.max(...intensities);
      const peakIdx = intensities.indexOf(maxVal);
      return { state, peakMonth: translateMonthShort(MONTHS_SHORT[peakIdx], locale), peakValue: maxVal };
    });

    // Density by region
    const regionLabels = Object.keys(regionMonthIntensity).sort();
    const totalByRegion = regionLabels.map(r => {
      const sum = regionMonthIntensity[r].reduce((a, b) => a + b, 0);
      return { name: translateRegion(r, locale), value: sum };
    });

    // Concentration index: states ranked by total activity
    const stateTotals = stateLabels.map(state => {
      const sum = stateMonthIntensity[state].reduce((a, b) => a + b, 0);
      return { name: state, value: sum };
    }).sort((a, b) => b.value - a.value);

    return {
      intensityMatrix: { z, states: stateLabels, months: MONTHS_SHORT.map((m) => translateMonthShort(m, locale)) },
      peakActivity: {
        categories: peakMonths.map(p => p.state),
        series: [{
          name: translateActivity('Peak Intensity', locale),
          values: peakMonths.map(p => p.peakValue),
        }],
      },
      densityByRegion: {
        labels: totalByRegion.map(r => r.name),
        values: totalByRegion.map(r => r.value),
      },
      concentrationIndex: {
        labels: stateTotals.map(s => s.name),
        values: stateTotals.map(s => s.value),
      },
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale]);

  const noData = intensityMatrix.states.length === 0;

  const intensityContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hIntensityMatrix')}</h3>
      {noData ? (
        <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
      ) : (
        <EChartsHeatmap
          z={intensityMatrix.z}
          x={intensityMatrix.months}
          y={intensityMatrix.states}
          captionKey="activityIntensity"
          height={Math.max(400, intensityMatrix.states.length * 25 + 100)}
        />
      )}
    </Card>
  );

  const peakContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hPeakActivity')}</h3>
      {noData ? (
        <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
      ) : (
        <EChartsGroupedBar
          categories={peakActivity.categories}
          series={peakActivity.series}
          captionKey="peakIntensity"
          height={Math.max(300, peakActivity.categories.length * 20 + 100)}
        />
      )}
    </Card>
  );

  const densityContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hDensityRegion')}</h3>
      {densityByRegion.values.length === 0 || densityByRegion.values.every(v => v === 0) ? (
        <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
      ) : (
        <EChartsHorizontalBar
          labels={densityByRegion.labels}
          values={densityByRegion.values}
          captionKey="totalActivity"
          height={Math.max(250, densityByRegion.labels.length * 40)}
        />
      )}
    </Card>
  );

  const concentrationContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hConcentration')}</h3>
      {concentrationIndex.values.length === 0 || concentrationIndex.values.every(v => v === 0) ? (
        <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
      ) : (
        <EChartsHorizontalBar
          labels={concentrationIndex.labels}
          values={concentrationIndex.values}
          captionKey="totalActivityScore"
          height={Math.max(300, concentrationIndex.labels.length * 25)}
        />
      )}
    </Card>
  );

  const subTabs = [
    { id: 'matrix', label: tBody('tabMatrix'), icon: BarChart3, content: intensityContent },
    { id: 'peak', label: tBody('tabPeak'), icon: Zap, content: peakContent },
    { id: 'density', label: tBody('tabDensity'), icon: Map, content: densityContent },
    { id: 'concentration', label: tBody('tabConcentration'), icon: TrendingUp, content: concentrationContent },
  ];

  return <Tabs tabs={subTabs} />;
}
