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
  translateCropName,
  translateMonthShort,
  translateRegion,
} from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { activityFromCode, type ConabCalendarRow } from '../../../types/calendar';
import { topUfsWithOverflow } from '../../../lib/calendarShare';

const MONTHS_FULL = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];
const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
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

    // Estado × mês: culturas com atividade (via schema Fase 1) → % das
    // culturas do escopo. Soma bruta vira share 0–100 com tooltip de culturas.
    const stateMonthCrops: Record<string, Set<string>[]> = {};
    const stateCropCount: Record<string, Set<string>> = {};
    const regionMonthIntensity: Record<string, number[]> = {};

    for (const row of rawData) {
      const crop = (row.crop || '').trim();
      if (!crop || !selectedCrops.includes(crop)) continue;

      const state = (row.uf || '').trim();
      if (!state) continue;
      const region = stateRegions[state];
      if (region && !selectedRegions.includes(region)) continue;

      if (!stateMonthCrops[state]) {
        stateMonthCrops[state] = MONTHS_FULL.map(() => new Set<string>());
      }
      if (!stateCropCount[state]) stateCropCount[state] = new Set();
      stateCropCount[state].add(crop);

      if (region && !regionMonthIntensity[region]) {
        regionMonthIntensity[region] = MONTHS_FULL.map(() => 0);
      }

      row.months.slice(0, 12).forEach((code, i) => {
        const { plantingPct, harvestPct } = activityFromCode(code);
        const intensity = plantingPct > 0 || harvestPct > 0 ? 1 : 0;
        if (intensity > 0) stateMonthCrops[state][i].add(crop);
        if (region) regionMonthIntensity[region][i] += intensity;
      });
    }

    // Intensity matrix: estados × meses em % de culturas ativas.
    const stateLabels = Object.keys(stateMonthCrops).sort();
    const scopeCrops = Math.max(selectedCrops.length, 1);
    const z: number[][] = stateLabels.map((s) =>
      stateMonthCrops[s].map((set) => Math.round((set.size / scopeCrops) * 100)),
    );
    const monthLabels = MONTHS_SHORT.map((m) => translateMonthShort(m, locale));
    const tips: (string | null)[][] = stateLabels.map((s) =>
      stateMonthCrops[s].map((set, i) => {
        if (set.size === 0) return null;
        const crops = [...set].map((c) => translateCropName(c, locale)).sort();
        const { top, overflow } = topUfsWithOverflow(crops, 5);
        const more = overflow > 0 ? ` ${tBody('ufsMore', { k: overflow })}` : '';
        return (
          `<b>${s} · ${monthLabels[i]}</b><br>` +
          `${Math.round((set.size / scopeCrops) * 100)}% (${set.size}/${scopeCrops})<br>` +
          `${top.join(', ')}${more}`
        );
      }),
    );

    // Peak activity: mês com maior % de culturas ativas por estado.
    const peakMonths = stateLabels.map((state, si) => {
      const shares = z[si] ?? [];
      const maxVal = shares.length > 0 ? Math.max(...shares) : 0;
      const peakIdx = Math.max(shares.indexOf(maxVal), 0);
      return { state, peakMonth: translateMonthShort(MONTHS_SHORT[peakIdx] ?? '', locale), peakValue: maxVal };
    });

    // Density by region
    const regionLabels = Object.keys(regionMonthIntensity).sort();
    const totalByRegion = regionLabels.map(r => {
      const sum = regionMonthIntensity[r].reduce((a, b) => a + b, 0);
      return { name: translateRegion(r, locale), value: sum };
    });

    // Concentration index: states ranked by total activity
    const stateTotals = stateLabels.map((state, si) => {
      const sum = (z[si] ?? []).reduce((a, b) => a + b, 0);
      return { name: state, value: sum };
    }).sort((a, b) => b.value - a.value);

    return {
      intensityMatrix: { z, tips, states: stateLabels, months: monthLabels },
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
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale, tBody]);

  const noData = intensityMatrix.states.length === 0;

  const intensityContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hIntensityMatrix')}</h3>
      {noData ? (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      ) : (
        <EChartsHeatmap
          z={intensityMatrix.z}
          x={intensityMatrix.months}
          y={intensityMatrix.states}
          captionKey="activityIntensity"
          height={Math.max(400, intensityMatrix.states.length * 25 + 100)}
          min={0}
          max={100}
          showValues
          valueSuffix="%"
          tips={intensityMatrix.tips}
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
