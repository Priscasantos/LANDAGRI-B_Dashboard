import { useMemo } from 'react';
import { BarChart3, GanttChart as GanttChartIcon, Target } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import EChartsLine from '../../charts/echarts/EChartsLine';
import EChartsGantt from '../../charts/echarts/EChartsGantt';
import EChartsPolar from '../../charts/echarts/EChartsPolar';
import { LANDAGRI_COLORWAY_DARK, LANDAGRI_COLORWAY_LIGHT } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateActivity,
  translateCropName,
  translateMonthShort,
} from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { bulletinIndexToMonth, type ConabCalendarRow } from '../../../types/calendar';
import {
  aggregateShares,
  bulletinSlotForMonth,
  currentCalendarMonth,
  recencyOf,
  toCalendarRecords,
  type MonthShare,
} from '../../../lib/calendarShare';
import RecencyBadge from './RecencyBadge';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
  crop_calendar?: Record<string, unknown[]>;
}

interface ActivitiesTimelineTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function ActivitiesTimelineTab({ selectedCrops, selectedRegions }: ActivitiesTimelineTabProps) {
  const { t: tBody, locale } = useT('agricultural');
  const theme = useEffectiveTheme();
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { monthlyActivity, ganttBars, polarData, recency, currentSlot, currentMonthLabel } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    const filtered = rawData.filter((row) => {
      const crop = (row.crop || '').trim();
      if (crop === '' || !selectedCrops.includes(crop)) return false;
      const state = (row.uf || '').trim();
      if (state === '') return false;
      const region = stateRegions[state];
      if (region !== undefined && !selectedRegions.includes(region)) return false;
      return true;
    });

    // % de UFs ativas por mês civil (ordem do boletim Out→Set no eixo).
    const records = toCalendarRecords(filtered);
    const global = aggregateShares(records);
    const pct = (civil: number, pick: (m: MonthShare) => number): number => {
      const share = global.find((m) => m.month === civil);
      return share === undefined ? 0 : Math.round(pick(share));
    };
    const months = MONTHS_SHORT.map((m) => translateMonthShort(m, locale));
    const civilOf = (slot: number): number => bulletinIndexToMonth(slot);
    const current = currentCalendarMonth();

    // Gantt por UF×cultura: janela primeiro→último slot ativo por atividade,
    // com tooltip % + contagem de UFs no mês de pico.
    const activeByCropStateActivity = new Map<string, { crop: string; state: string; kind: 'P' | 'H'; slots: number[] }>();
    for (const row of filtered) {
      const crop = (row.crop || '').trim();
      const state = (row.uf || '').trim();
      row.months.slice(0, 12).forEach((code, slot) => {
        const v = (code || '').trim().toUpperCase();
        const kinds: ('P' | 'H')[] = [];
        if (v === 'P' || v === 'PH') kinds.push('P');
        if (v === 'H' || v === 'PH') kinds.push('H');
        for (const kind of kinds) {
          const key = `${crop}¦${state}¦${kind}`;
          const entry = activeByCropStateActivity.get(key) ?? { crop, state, kind, slots: [] };
          entry.slots.push(slot);
          activeByCropStateActivity.set(key, entry);
        }
      });
    }
    const ganttEntries: { label: string; start: number; end: number; category: string; tip: string }[] = [];
    for (const entry of activeByCropStateActivity.values()) {
      const first = Math.min(...entry.slots);
      const last = Math.max(...entry.slots);
      ganttEntries.push({
        label: `${translateCropName(entry.crop, locale)} ${entry.kind} (${entry.state})`,
        start: first,
        end: last + 0.5,
        category: translateCropName(entry.crop, locale),
        tip:
          `<b>${translateCropName(entry.crop, locale)} ${entry.kind} (${entry.state})</b><br>` +
          `${months[first]} – ${months[last]}`,
      });
    }

    return {
      monthlyActivity: {
        series: [
          {
            name: translateActivity('Planting', locale),
            x: months,
            y: MONTHS_SHORT.map((_, slot) => pct(civilOf(slot), (m) => m.pctPlanting)),
          },
          {
            name: translateActivity('Harvest', locale),
            x: months,
            y: MONTHS_SHORT.map((_, slot) => pct(civilOf(slot), (m) => m.pctHarvest)),
          },
        ],
      },
      ganttBars: ganttEntries.slice(0, 100),
      polarData: {
        series: [{
          name: translateActivity('Total Activity', locale),
          r: MONTHS_SHORT.map((_, slot) => pct(civilOf(slot), (m) => m.pctActive)),
          theta: months,
          fill: 'toself' as const,
        }],
      },
      recency: recencyOf(records),
      currentSlot: bulletinSlotForMonth(current),
      currentMonthLabel: months[bulletinSlotForMonth(current)] ?? '',
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale]);

  const way = theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;

  const monthlyContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hMonthlySeasonality')}</h3>
      <EChartsLine
        series={monthlyActivity.series.map((s, i) => ({ ...s, color: i === 0 ? way[0] : way[5] }))}
        captionKey="shareSplitMonthly"
        height={400}
        yMin={0}
        yMax={100}
        markLineX={{ x: currentMonthLabel, name: tBody('currentMonth') }}
      />
      <div className="mt-3">
        <RecencyBadge recency={recency} />
      </div>
    </Card>
  );

  const ganttContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hPlantingHarvest')}</h3>
      {ganttBars.length > 0 ? (
        <EChartsGantt
          bars={ganttBars}
          xLabels={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
          captionKey="monthAxisNote"
          height={Math.min(600, Math.max(300, ganttBars.length * 12))}
          markLineX={{ position: currentSlot + 0.5, name: tBody('currentMonth') }}
        />
      ) : (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      )}
    </Card>
  );

  const polarContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('tabPolar')}</h3>
      {polarData.series[0].r.some(v => (v ?? 0) > 0) ? (
        <EChartsPolar
          series={polarData.series}
          categories={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
          captionKey="seasonalActivityDistribution"
          height={500}
        />
      ) : (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      )}
    </Card>
  );

  const subTabs = [
    { id: 'monthly', label: tBody('hMonthlySeasonality'), icon: BarChart3, content: monthlyContent },
    { id: 'gantt', label: tBody('tabGantt'), icon: GanttChartIcon, content: ganttContent },
    { id: 'polar', label: tBody('tabPolar'), icon: Target, content: polarContent },
  ];

  return <Tabs tabs={subTabs} />;
}
