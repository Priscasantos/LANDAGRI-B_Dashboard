import { useMemo } from 'react';
import { BarChart3, GanttChart as GanttChartIcon, Target } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import EChartsLine from '../../charts/echarts/EChartsLine';
import EChartsGantt from '../../charts/echarts/EChartsGantt';
import EChartsPolar from '../../charts/echarts/EChartsPolar';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateActivity,
  translateCropName,
  translateMonthShort,
} from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import type { ConabCalendarRow } from '../../../types/calendar';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];
const MONTHS_FULL = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
  crop_calendar?: Record<string, unknown[]>;
}

function parseActivityValue(val: string): number {
  if (!val || val.trim() === '') return 0;
  const v = val.trim();
  if (v === 'PH') return 3;
  if (v === 'P') return 1;
  if (v === 'H') return 2;
  return 0;
}

interface ActivitiesTimelineTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function ActivitiesTimelineTab({ selectedCrops, selectedRegions }: ActivitiesTimelineTabProps) {
  const { t: tBody, locale } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const { monthlyActivity, ganttBars, polarData } = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    const plantCount = MONTHS_FULL.map(() => 0);
    const harvestCount = MONTHS_FULL.map(() => 0);
    const ganttEntries: { label: string; start: number; end: number; category: string }[] = [];
    const polarR: number[] = MONTHS_FULL.map(() => 0);

    for (const row of rawData) {
      const crop = (row.crop || '').trim();
      if (!crop || !selectedCrops.includes(crop)) continue;

      const state = (row.uf || '').trim();
      if (!state) continue;
      const region = stateRegions[state];
      if (region && !selectedRegions.includes(region)) continue;

      const activities = row.months.map((v) => parseActivityValue(v));

      let firstPlanting = -1;
      let lastPlanting = -1;
      let firstHarvest = -1;
      let lastHarvest = -1;

      activities.forEach((val, i) => {
        if (val === 1 || val === 3) {
          plantCount[i]++;
          if (firstPlanting === -1) firstPlanting = i;
          lastPlanting = i;
        }
        if (val === 2 || val === 3) {
          harvestCount[i]++;
          if (firstHarvest === -1) firstHarvest = i;
          lastHarvest = i;
        }
        if (val > 0) polarR[i]++;
      });

      if (firstPlanting >= 0) {
        ganttEntries.push({
          label: `${translateCropName(crop, locale)} P (${state})`,
          start: firstPlanting,
          end: lastPlanting + 0.5,
          category: translateCropName(crop, locale),
        });
      }
      if (firstHarvest >= 0) {
        ganttEntries.push({
          label: `${translateCropName(crop, locale)} H (${state})`,
          start: firstHarvest,
          end: lastHarvest + 0.5,
          category: translateCropName(crop, locale),
        });
      }
    }

    return {
      monthlyActivity: {
        series: [
          { name: translateActivity('Planting', locale), x: MONTHS_SHORT.map((m) => translateMonthShort(m, locale)), y: plantCount },
          { name: translateActivity('Harvest', locale), x: MONTHS_SHORT.map((m) => translateMonthShort(m, locale)), y: harvestCount },
        ],
      },
      ganttBars: ganttEntries.slice(0, 100),
      polarData: {
        series: [{
          name: translateActivity('Total Activity', locale),
          r: polarR,
          theta: MONTHS_SHORT.map((m) => translateMonthShort(m, locale)),
          fill: 'toself' as const,
        }],
      },
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale]);

  const monthlyContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hMonthlySeasonality')}</h3>
      <EChartsLine
        series={monthlyActivity.series}
        captionKey="activityCount"
        height={400}
      />
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
        />
      ) : (
        <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
      )}
    </Card>
  );

  const polarContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hPolarSeasonality')}</h3>
      {polarData.series[0].r.some(v => v > 0) ? (
        <EChartsPolar
          series={polarData.series}
          categories={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
          captionKey="seasonalActivityDistribution"
          height={500}
        />
      ) : (
        <p className="text-fg-muted text-center py-8">{tBody('noFilterData')}</p>
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
