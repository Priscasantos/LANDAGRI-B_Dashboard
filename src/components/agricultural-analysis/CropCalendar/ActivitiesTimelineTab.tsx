import { useMemo } from 'react';
import { BarChart3, GanttChart as GanttChartIcon, Target } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import LineChart from '../../charts/LineChart';
import GanttChart from '../../charts/GanttChart';
import PolarChart from '../../charts/PolarChart';
import { useT } from '../../../i18n/LanguageContext';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];
const MONTHS_FULL = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];

interface CalendarRow {
  'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September': string;
}

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
  const { t } = useT('charts');
  const { t: tBody } = useT('agricultural');
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
      const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
      if (!entry || entry.trim() === '' || entry.startsWith(';')) continue;

      const parts = entry.split(';');
      if (parts.length < 13) continue;

      const crop = parts[0].trim();
      if (!crop || !selectedCrops.includes(crop)) continue;

      const state = parts[1].trim();
      const region = stateRegions[state];
      if (region && !selectedRegions.includes(region)) continue;

      const activities = parts.slice(2).map(v => parseActivityValue(v));

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
          label: `${crop} P (${state})`,
          start: firstPlanting,
          end: lastPlanting + 0.5,
          category: crop,
        });
      }
      if (firstHarvest >= 0) {
        ganttEntries.push({
          label: `${crop} H (${state})`,
          start: firstHarvest,
          end: lastHarvest + 0.5,
          category: crop,
        });
      }
    }

    return {
      monthlyActivity: {
        series: [
          { name: 'Planting', x: MONTHS_SHORT, y: plantCount, color: '#22c55e' },
          { name: 'Harvest', x: MONTHS_SHORT, y: harvestCount, color: '#f97316' },
        ],
      },
      ganttBars: ganttEntries.slice(0, 100),
      polarData: {
        series: [{
          name: 'Total Activity',
          r: polarR,
          theta: MONTHS_SHORT,
          fill: 'toself' as const,
        }],
      },
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const monthlyContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hMonthlySeasonality')}</h3>
      <LineChart
        series={monthlyActivity.series}
        xlabel={t('month')}
        ylabel={t('activityCount')}
        height={400}
      />
    </Card>
  );

  const ganttContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('hPlantingHarvest')}</h3>
      {ganttBars.length > 0 ? (
        <GanttChart
          bars={ganttBars}
          xlabel={t('monthAxisNote')}
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
        <PolarChart
          series={polarData.series}
          title={t('seasonalActivityDistribution')}
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
