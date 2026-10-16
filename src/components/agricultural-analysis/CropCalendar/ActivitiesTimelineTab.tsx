import { useMemo, useState } from 'react';
import { BarChart3, GanttChart as GanttChartIcon, Target } from 'lucide-react';
import Tabs from '../../ui/Tabs';
import Card from '../../ui/Card';
import EChartsLine from '../../charts/echarts/EChartsLine';
import EChartsPhenoGantt from '../../charts/echarts/EChartsPhenoGantt';
import EChartsPolar from '../../charts/echarts/EChartsPolar';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateActivity,
  translateCropName,
  translateMonthShort,
  translateRegion,
} from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { bulletinIndexToMonth, type ConabCalendarRow } from '../../../types/calendar';
import {
  aggregateSharesWithMode,
  bulletinSlotForMonth,
  currentCalendarMonth,
  recencyOf,
  resolveShareMode,
  toCalendarRecords,
  type MonthShare,
  type ShareMode,
} from '../../../lib/calendarShare';
import {
  MAX_PHENO_LANES,
  buildPhenoModel,
  formatPhenoTip,
  seasonLabelForDate,
  type PhenoTipLabels,
} from '../../../lib/phenoGantt';
import { phenoPhaseColor } from '../../../lib/phenoColors';
import RecencyBadge from './RecencyBadge';
import ShareModeToggle from './ShareModeToggle';
import PhenologyLegend from './PhenologyLegend';

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
  // Congelado por render: `{}` literal recriado invalidaria o useMemo abaixo.
  const statesMap = useMemo(() => mappingData?.states ?? {}, [mappingData]);
  // Toggle % UFs vs % área: default área quando há `areaSharePct`, senão UFs rotulado.
  const [modeOverride, setModeOverride] = useState<ShareMode | null>(null);

  const {
    monthlyActivity,
    phenoLanes,
    phenoLaneKinds,
    phenoSegments,
    lanesNote,
    polarData,
    recency,
    currentSlot,
    currentMonthLabel,
    shareMode,
    shareHasArea,
  } = useMemo(() => {
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

    // % por mês civil com modo explícito (ordem do boletim Out→Set no eixo).
    const records = toCalendarRecords(filtered);
    const requested: ShareMode = modeOverride ?? resolveShareMode(records);
    const { shares: global, effective, hasArea } = aggregateSharesWithMode(records, requested);
    const pct = (civil: number, pick: (m: MonthShare) => number): number => {
      const share = global.find((m) => m.month === civil);
      return share === undefined ? 0 : Math.round(pick(share));
    };
    const months = MONTHS_SHORT.map((m) => translateMonthShort(m, locale));
    const civilOf = (slot: number): number => bulletinIndexToMonth(slot);
    const current = currentCalendarMonth();

    // Gantt fenológico: duas lanes (P/H) por cultura-região com segmentos
    // disjuntos (hiato nunca colapsa); PH vira faixa hachurada própria.
    const pheno = buildPhenoModel(filtered, stateRegions);
    const shownLanes = pheno.lanes.slice(0, MAX_PHENO_LANES);
    const shownIds = new Set(shownLanes.map((l) => l.id));
    const laneLabels = shownLanes.map(
      (l) => `${translateCropName(l.crop, locale)} · ${l.kind} · ${translateRegion(l.region, locale)}`,
    );
    const tipLabels: PhenoTipLabels = {
      planting: translateActivity('Planting', locale),
      harvest: translateActivity('Harvest', locale),
      activeUfs: (active, total) => `${active}/${total} ${tBody('activeUfsLabel')}`,
      simultaneous: tBody('legendBothNote'),
      more: (k) => tBody('ufsMore', { k }),
    };
    const segments = pheno.segments
      .filter((s) => shownIds.has(s.laneId))
      .map((s) => {
        const lane = shownLanes.findIndex((l) => l.id === s.laneId);
        return {
          lane,
          start: s.start,
          end: s.end,
          ph: s.ph,
          tip: formatPhenoTip(s, laneLabels[lane] ?? s.laneId, months, tipLabels),
        };
      });

    // Relógio fenológico: radial mês-circular (raio = % em P/H por série).
    const plantingR = MONTHS_SHORT.map((_, slot) => pct(civilOf(slot), (m) => m.pctPlanting));
    const harvestR = MONTHS_SHORT.map((_, slot) => pct(civilOf(slot), (m) => m.pctHarvest));

    return {
      monthlyActivity: {
        series: [
          {
            name: translateActivity('Planting', locale),
            x: months,
            y: plantingR,
            color: phenoPhaseColor('P', theme),
          },
          {
            name: translateActivity('Harvest', locale),
            x: months,
            y: harvestR,
            color: phenoPhaseColor('H', theme),
          },
        ],
      },
      phenoLanes: laneLabels,
      phenoLaneKinds: shownLanes.map((l) => l.kind),
      phenoSegments: segments,
      lanesNote:
        pheno.lanes.length > shownLanes.length
          ? tBody('ganttLanesNote', { shown: shownLanes.length, total: pheno.lanes.length })
          : null,
      polarData: {
        series: [
          { name: translateActivity('Planting', locale), r: plantingR, color: phenoPhaseColor('P', theme) },
          { name: translateActivity('Harvest', locale), r: harvestR, color: phenoPhaseColor('H', theme) },
        ],
      },
      recency: recencyOf(records),
      currentSlot: bulletinSlotForMonth(current),
      currentMonthLabel: months[bulletinSlotForMonth(current)] ?? '',
      shareMode: effective,
      shareHasArea: hasArea,
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale, theme, tBody, modeOverride]);

  const seasonBadge = tBody('seasonBadge', {
    season: seasonLabelForDate(new Date()),
    month: currentMonthLabel,
  });

  const monthlyContent = (
    <Card padding="lg" hover={false}>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hMonthlySeasonality')}</h3>
        <ShareModeToggle mode={shareMode} hasArea={shareHasArea} onChange={setModeOverride} />
      </div>
      <EChartsLine
        series={monthlyActivity.series}
        captionKey="shareSplitMonthly"
        height={400}
        yMin={0}
        yMax={100}
        markLineX={{ x: currentMonthLabel, name: tBody('currentMonth') }}
      />
      <div className="mt-3 space-y-2">
        <PhenologyLegend />
        <RecencyBadge recency={recency} />
      </div>
    </Card>
  );

  const ganttContent = (
    <Card padding="lg" hover={false}>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hPlantingHarvest')}</h3>
        <span className="rounded-full bg-brand/10 px-3 py-1 text-xs font-semibold text-brand" role="status">
          {seasonBadge}
        </span>
      </div>
      {phenoSegments.length > 0 ? (
        <>
          <EChartsPhenoGantt
            lanes={phenoLanes}
            laneKinds={phenoLaneKinds}
            xLabels={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
            segments={phenoSegments}
            seasonBandEnd={currentSlot + 0.5}
            seasonBandName={tBody('seasonBand')}
            todayPosition={currentSlot + 0.5}
            todayName={tBody('today')}
            captionKey="monthAxisNote"
            height={Math.min(600, Math.max(300, phenoLanes.length * 28))}
          />
          <div className="mt-3 space-y-2">
            <PhenologyLegend />
            {lanesNote !== null && (
              <p className="text-xs text-fg-muted" role="status">
                {lanesNote}
              </p>
            )}
          </div>
        </>
      ) : (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      )}
    </Card>
  );

  const polarContent = (
    <Card padding="lg" hover={false}>
      <h3 className="text-base font-semibold text-fg mb-3">{tBody('tabPolar')}</h3>
      {polarData.series.some((s) => s.r.some((v) => (v ?? 0) > 0)) ? (
        <>
          <EChartsPolar
            series={polarData.series}
            categories={MONTHS_SHORT.map((m) => translateMonthShort(m, locale))}
            captionKey="seasonalActivityDistribution"
            height={500}
          />
          <div className="mt-3">
            <PhenologyLegend />
          </div>
        </>
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
