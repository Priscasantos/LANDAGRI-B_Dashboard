import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsLine from '../../charts/echarts/EChartsLine';
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
  aggregateSharesByGroup,
  bulletinSlotForMonth,
  currentCalendarMonth,
  formatShareTip,
  recencyOf,
  toCalendarRecords,
  type MonthShare,
  type ShareTipLabels,
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
}

interface MonthlyIntensityTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function MonthlyIntensityTab({ selectedCrops, selectedRegions }: MonthlyIntensityTabProps) {
  const { t: tBody, locale } = useT('agricultural');
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const model = useMemo(() => {
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

    const records = toCalendarRecords(filtered);
    return {
      records,
      byCrop: aggregateSharesByGroup(records, (r) => r.cropId),
      global: aggregateShares(records),
      recency: recencyOf(records),
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const tipLabels: ShareTipLabels = {
    activeUfs: tBody('activeUfsLabel'),
    planting: tBody('tipPlanting'),
    harvest: tBody('tipHarvest'),
    more: (k) => tBody('ufsMore', { k }),
  };

  const currentMonth = currentCalendarMonth();
  const currentSlot = bulletinSlotForMonth(currentMonth);
  const monthLabels = MONTHS_SHORT.map((m, slot) => {
    const label = translateMonthShort(m, locale);
    return slot === currentSlot ? `${label} ●` : label;
  });

  const cropKeys = selectedCrops.filter((crop) => model.byCrop.has(crop));
  const z: number[][] = cropKeys.map((crop) =>
    MONTHS_SHORT.map((_, slot) => {
      const civil = bulletinIndexToMonth(slot);
      return Math.round(model.byCrop.get(crop)?.find((m: MonthShare) => m.month === civil)?.pctActive ?? 0);
    }),
  );
  const tips: (string | null)[][] = cropKeys.map((crop) =>
    MONTHS_SHORT.map((_, slot) => {
      const civil = bulletinIndexToMonth(slot);
      const share = model.byCrop.get(crop)?.find((m: MonthShare) => m.month === civil);
      if (share === undefined || share.totalUfs === 0) return null;
      return formatShareTip(`${translateCropName(crop, locale)} · ${monthLabels[slot]}`, share, tipLabels);
    }),
  );

  const intensityY = MONTHS_SHORT.map((_, slot) => {
    const civil = bulletinIndexToMonth(slot);
    return Math.round(model.global.find((m) => m.month === civil)?.pctActive ?? 0);
  });
  const noData = cropKeys.length === 0 || intensityY.every((v) => v === 0);

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="text-base font-semibold text-fg">{tBody('hMonthlyHeatmap')}</h3>
          <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
        </div>
        {noData ? (
          <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
        ) : (
          <>
            <EChartsHeatmap
              z={z}
              x={monthLabels}
              y={cropKeys.map((crop) => translateCropName(crop, locale))}
              captionKey="activityIntensityCropsMonths"
              height={Math.max(300, cropKeys.length * 40 + 100)}
              min={0}
              max={100}
              showValues
              valueSuffix="%"
              tips={tips}
            />
            <div className="mt-3">
              <RecencyBadge recency={model.recency} />
            </div>
          </>
        )}
      </Card>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hIntensityByMonth')}</h3>
        {noData ? (
          <p className="text-fg-muted text-center py-8" role="status">{tBody('noData')}</p>
        ) : (
          <EChartsLine
            series={[{
              name: translateActivity('Activity Intensity', locale),
              x: monthLabels,
              y: intensityY,
            }]}
            captionKey="shareActiveUfs"
            height={350}
            yMin={0}
            yMax={100}
            markLineX={{ x: monthLabels[currentSlot] ?? '', name: tBody('currentMonth') }}
          />
        )}
      </Card>
    </div>
  );
}
