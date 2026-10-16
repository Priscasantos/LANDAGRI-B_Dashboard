import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsGantt from '../../charts/echarts/EChartsGantt';
import { LANDAGRI_COLORWAY_DARK, LANDAGRI_COLORWAY_LIGHT } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName, translateMonthShort } from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { activityFromCode, type ConabCalendarRow } from '../../../types/calendar';
import { bulletinSlotForMonth, currentCalendarMonth } from '../../../lib/calendarShare';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
}

function parseActivityValue(val: string): number {
  const { plantingPct, harvestPct } = activityFromCode(val);
  return plantingPct > 0 || harvestPct > 0 ? 1 : 0;
}

interface SpatioTemporalTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function SpatioTemporalTab({ selectedCrops, selectedRegions }: SpatioTemporalTabProps) {
  const { t } = useT('charts');
  const { t: tBody, locale } = useT('agricultural');
  const theme = useEffectiveTheme();
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { bars, legend } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Track per-state per-crop: which months are active
    const stateCropMonths: Record<string, Record<string, Set<number>>> = {};

    for (const row of rawData) {
      const crop = (row.crop || '').trim();
      if (!crop || !selectedCrops.includes(crop)) continue;

      const state = (row.uf || '').trim();
      if (!state) continue;
      const region = stateRegions[state];
      if (region && !selectedRegions.includes(region)) continue;

      if (!stateCropMonths[state]) stateCropMonths[state] = {};
      if (!stateCropMonths[state][crop]) stateCropMonths[state][crop] = new Set();

      row.months.forEach((v, i) => {
        if (parseActivityValue(v) > 0) {
          stateCropMonths[state][crop].add(i);
        }
      });
    }

    // One Gantt bar per state: active period tinted by dominant crop
    // (same crop → same slot of the active theme colorway, light/dark aware).
    const way = theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;
    const bars: { label: string; start: number; end: number; color: string; tip: string }[] = [];
    const stateNames = Object.keys(stateCropMonths).sort();
    const monthLabels = MONTHS_SHORT.map((m) => translateMonthShort(m, locale));

    stateNames.forEach((state) => {
      const monthsSet = new Set<number>();
      const cropColors = new Map<string, string>();

      for (const [crop, mSet] of Object.entries(stateCropMonths[state])) {
        mSet.forEach(m => monthsSet.add(m));
        cropColors.set(crop, way[selectedCrops.indexOf(crop) % way.length]);
      }

      if (monthsSet.size === 0) return;

      const sortedMonths = Array.from(monthsSet).sort((a, b) => a - b);
      const firstMonth = sortedMonths[0];
      const lastMonth = sortedMonths[sortedMonths.length - 1];
      const dominantCrop = [...cropColors.entries()]
        .sort((a, b) => stateCropMonths[state][b[0]]?.size || 0 - (stateCropMonths[state][a[0]]?.size || 0))[0]?.[0] || '';
      const color = cropColors.get(dominantCrop) ?? way[0];

      bars.push({
        label: state,
        start: firstMonth,
        end: lastMonth + 1,
        color,
        tip: `<b>${state}</b><br>${t('period')}: ${monthLabels[firstMonth]} – ${monthLabels[lastMonth]}<br>${t('crop')}: ${translateCropName(dominantCrop, locale)}`,
      });
    });

    // Legenda: cor por cultura dominante (mesmo slot do colorway usado nas barras).
    const legend = selectedCrops
      .filter((crop) => Object.values(stateCropMonths).some((byCrop) => (byCrop[crop]?.size ?? 0) > 0))
      .map((crop, i) => ({
        crop,
        label: translateCropName(crop, locale),
        color: way[selectedCrops.indexOf(crop) % way.length] ?? way[i % way.length],
      }));

    return { bars, legend };
  }, [rawData, selectedCrops, selectedRegions, statesMap, t, locale, theme]);

  return (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSpatioTemporal')}</h3>
      {bars.length > 0 ? (
        <>
          <EChartsGantt
            bars={bars}
            xLabels={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
            captionKey="spatioTemporalDistribution"
            height={Math.max(400, bars.length * 25 + 100)}
            markLineX={{ position: bulletinSlotForMonth(currentCalendarMonth()) + 0.5, name: tBody('currentMonth') }}
          />
          {legend.length > 0 ? (
            <div className="mt-3 flex flex-wrap items-center gap-x-4 gap-y-1" role="group" aria-label={t('legend')}>
              <span className="text-xs font-medium text-fg-secondary">{t('legend')}:</span>
              <ul className="flex flex-wrap items-center gap-x-4 gap-y-1">
                {legend.map((entry) => (
                  <li key={entry.crop} className="flex items-center gap-1.5 text-xs text-fg-secondary">
                    <span
                      aria-hidden="true"
                      className="inline-block h-3 w-3 rounded-sm"
                      style={{ backgroundColor: entry.color }}
                    />
                    {entry.label}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </>
      ) : (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      )}
    </Card>
  );
}
