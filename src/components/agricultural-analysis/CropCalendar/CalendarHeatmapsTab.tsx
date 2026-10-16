import { useMemo } from 'react';
import { Info } from 'lucide-react';
import Card from '../../ui/Card';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { LANDAGRI_COLORWAY_DARK, LANDAGRI_COLORWAY_LIGHT } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName, translateMonth } from '../../../data/glossary';
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
  resolveShareMode,
  toCalendarRecords,
  type MonthShare,
  type ShareTipLabels,
} from '../../../lib/calendarShare';
import RecencyBadge from './RecencyBadge';

const MONTHS = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  metadata?: Record<string, unknown>;
  states?: Record<string, StateInfo>;
  crop_calendar?: Record<string, unknown[]>;
}

interface CalendarHeatmapsTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function CalendarHeatmapsTab({ selectedCrops, selectedRegions }: CalendarHeatmapsTabProps) {
  const { t } = useT('charts');
  const { t: tBody, locale } = useT('agricultural');
  const theme = useEffectiveTheme();
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const model = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Filtro sobre campos tipados (sem parse ad-hoc); normalização via schema Fase 1.
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
    const byCrop = aggregateSharesByGroup(records, (r) => r.cropId);
    const global = aggregateShares(records);
    return { records, byCrop, global, mode: resolveShareMode(records), recency: recencyOf(records) };
  }, [rawData, selectedCrops, selectedRegions, statesMap]);

  const tipLabels: ShareTipLabels = {
    activeUfs: tBody('activeUfsLabel'),
    planting: tBody('tipPlanting'),
    harvest: tBody('tipHarvest'),
    more: (k) => tBody('ufsMore', { k }),
  };

  const currentMonth = currentCalendarMonth();
  const currentSlot = bulletinSlotForMonth(currentMonth);
  const monthLabels = MONTHS.map((m, slot) => {
    const label = translateMonth(m, locale);
    return slot === currentSlot ? `${label} ●` : label;
  });

  const cropKeys = selectedCrops.filter((crop) => model.byCrop.has(crop));
  const z: number[][] = cropKeys.map((crop) => {
    const shares = model.byCrop.get(crop);
    if (shares === undefined) return MONTHS.map(() => 0);
    return MONTHS.map((_, slot) => {
      const civil = bulletinIndexToMonth(slot);
      return Math.round(shares.find((m: MonthShare) => m.month === civil)?.pctActive ?? 0);
    });
  });
  const tips: (string | null)[][] = cropKeys.map((crop) =>
    MONTHS.map((_, slot) => {
      const civil = bulletinIndexToMonth(slot);
      const share = model.byCrop.get(crop)?.find((m: MonthShare) => m.month === civil);
      if (share === undefined || share.totalUfs === 0) return null;
      return formatShareTip(`${translateCropName(crop, locale)} · ${monthLabels[slot]}`, share, tipLabels);
    }),
  );
  const cropLabels = cropKeys.map((crop) => translateCropName(crop, locale));

  // Split P/H por mês (global, ordem do boletim): barras empilhadas % plantio + % colheita.
  const plantSeries = MONTHS.map((_, slot) => {
    const civil = bulletinIndexToMonth(slot);
    return Math.round(model.global.find((m) => m.month === civil)?.pctPlanting ?? 0);
  });
  const harvestSeries = MONTHS.map((_, slot) => {
    const civil = bulletinIndexToMonth(slot);
    return Math.round(model.global.find((m) => m.month === civil)?.pctHarvest ?? 0);
  });

  const way = theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;
  const plantingColor = way[0];
  const harvestColor = way[5];
  const emptyCell = theme === 'dark' ? '#1e293b' : '#f1f5f9';

  if (cropKeys.length === 0) {
    return (
      <Card padding="lg" hover={false}>
        <div className="p-8 text-center text-fg-secondary">
          <p role="status">{tBody('noCalendarData')}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
          <h3 className="text-base font-semibold text-fg">{tBody('hNationalMatrix')}</h3>
          <span className="inline-flex items-center gap-1 text-xs font-medium text-fg-secondary">
            {model.mode === 'area' ? tBody('shareModeArea') : tBody('shareModeUf')}
            <button
              type="button"
              title={tBody('shareScaleNote')}
              aria-label={tBody('shareScaleNote')}
              className="inline-flex cursor-help items-center justify-center rounded-full text-fg-secondary hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2"
            >
              <Info size={14} aria-hidden="true" />
            </button>
          </span>
        </div>
        <EChartsHeatmap
          z={z}
          x={monthLabels}
          y={cropLabels}
          captionKey="cropCalendarActivity"
          height={Math.max(300, cropLabels.length * 50 + 100)}
          min={0}
          max={100}
          showValues
          valueSuffix="%"
          tips={tips}
        />
        <div className="mt-3">
          <RecencyBadge recency={model.recency} />
        </div>
      </Card>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hMonthlySeasonality')}</h3>
        <EChartsGroupedBar
          categories={monthLabels}
          series={[
            { name: t('planting'), values: plantSeries, color: plantingColor },
            { name: t('harvest'), values: harvestSeries, color: harvestColor },
          ]}
          stacked
          captionKey="activityCount"
          height={360}
        />
      </Card>

      {/* Legenda única: vale para o heatmap (%) e para o split P/H empilhado. */}
      <Card padding="md" hover={false}>
        <div className="flex items-center gap-6 flex-wrap" role="list" aria-label={t('legend')}>
          <span className="text-sm font-medium text-fg-secondary">{t('legend')}:</span>
          <div className="flex items-center gap-2" role="listitem">
            <span className="w-4 h-4 rounded inline-block" style={{ backgroundColor: plantingColor }} aria-hidden="true" />
            <span className="text-xs text-fg-secondary">{t('planting')}</span>
          </div>
          <div className="flex items-center gap-2" role="listitem">
            <span className="w-4 h-4 rounded inline-block" style={{ backgroundColor: harvestColor }} aria-hidden="true" />
            <span className="text-xs text-fg-secondary">{t('harvest')}</span>
          </div>
          <div className="flex items-center gap-2" role="listitem">
            <span className="w-4 h-4 rounded inline-block border border-border" style={{ backgroundColor: emptyCell }} aria-hidden="true" />
            <span className="text-xs text-fg-secondary">{t('noActivity')}</span>
          </div>
          <span className="text-xs text-fg-secondary" role="listitem">
            ● = {tBody('currentMonth')}
          </span>
        </div>
      </Card>
    </div>
  );
}
