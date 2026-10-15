import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsGantt from '../../charts/echarts/EChartsGantt';
import { CATEGORICAL_COLORS } from '../../../types/theme';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName, translateMonthShort } from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';

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
  if (v === 'P' || v === 'H' || v === 'PH') return 1;
  return 0;
}

interface SpatioTemporalTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function SpatioTemporalTab({ selectedCrops, selectedRegions }: SpatioTemporalTabProps) {
  const { t } = useT('charts');
  const { t: tBody, locale } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const chartData = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Track per-state per-crop: which months are active
    const stateCropMonths: Record<string, Record<string, Set<number>>> = {};

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

      if (!stateCropMonths[state]) stateCropMonths[state] = {};
      if (!stateCropMonths[state][crop]) stateCropMonths[state][crop] = new Set();

      parts.slice(2).forEach((v, i) => {
        if (parseActivityValue(v) > 0) {
          stateCropMonths[state][crop].add(i);
        }
      });
    }

    // One Gantt bar per state: active period tinted by dominant crop
    const bars: { label: string; start: number; end: number; color: string; tip: string }[] = [];
    const stateNames = Object.keys(stateCropMonths).sort();

    stateNames.forEach((state, idx) => {
      const monthsSet = new Set<number>();
      const cropColors = new Map<string, string>();

      for (const [crop, mSet] of Object.entries(stateCropMonths[state])) {
        mSet.forEach(m => monthsSet.add(m));
        cropColors.set(crop, CATEGORICAL_COLORS[selectedCrops.indexOf(crop) % CATEGORICAL_COLORS.length]);
      }

      if (monthsSet.size === 0) return;

      const sortedMonths = Array.from(monthsSet).sort((a, b) => a - b);
      const firstMonth = sortedMonths[0];
      const lastMonth = sortedMonths[sortedMonths.length - 1];
      const dominantCrop = [...cropColors.entries()]
        .sort((a, b) => stateCropMonths[state][b[0]]?.size || 0 - (stateCropMonths[state][a[0]]?.size || 0))[0]?.[0] || '';
      const color = cropColors.get(dominantCrop) || CATEGORICAL_COLORS[idx % CATEGORICAL_COLORS.length];

      bars.push({
        label: state,
        start: firstMonth,
        end: lastMonth + 1,
        color,
        tip: `<b>${state}</b><br>${t('period')}: ${firstMonth}-${lastMonth}<br>${t('crop')}: ${translateCropName(dominantCrop, locale)}`,
      });
    });

    return bars;
  }, [rawData, selectedCrops, selectedRegions, statesMap, t, locale]);

  return (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSpatioTemporal')}</h3>
      {chartData.length > 0 ? (
        <EChartsGantt
          bars={chartData}
          xLabels={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
          captionKey="spatioTemporalDistribution"
          height={Math.max(400, chartData.length * 25 + 100)}
        />
      ) : (
        <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
      )}
    </Card>
  );
}
