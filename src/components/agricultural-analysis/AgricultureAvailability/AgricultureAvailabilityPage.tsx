import { useMemo, useState, type ReactElement } from 'react';
import { ChevronDown, Map, Wheat, MapPin } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import conabAvailability from '../../../data/processed/conab_availability.json';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import type {
  ConabAvailabilityRow,
  ConabCalendarRow,
} from '../../../types/calendar';
import { bulletinIndexToMonth } from '../../../types/calendar';
import {
  aggregateSharesByGroup,
  bulletinSlotForMonth,
  currentCalendarMonth,
  formatShareTip,
  recencyOf,
  toCalendarRecords,
  type MonthShare,
  type ShareTipLabels,
} from '../../../lib/calendarShare';
import RecencyBadge from '../CropCalendar/RecencyBadge';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateCropName,
  translateMonthShort,
  translateRegion,
} from '../../../data/glossary';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

type AvailabilityRow = ConabAvailabilityRow;

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
}

const ALL = 'all';

/** Typed accessors over `conab_availability.json` (no `;`-joined fallback). */
function availCrop(row: AvailabilityRow): string {
  const crop = (row.crop || '').trim();
  return crop !== '' ? crop : 'Unknown';
}

function availUf(row: AvailabilityRow): string {
  return (row.uf || '').trim();
}

function availPeriods(row: AvailabilityRow): string[] {
  return [...(row.anos_1s ?? []), ...(row.anos_2s ?? [])].map((p) => p.trim()).filter(Boolean);
}

function calendarUf(row: CalendarRow): string {
  return (row.uf || '').trim();
}

function calendarCrop(row: CalendarRow): string {
  return (row.crop || '').trim();
}

/**
 * P2a: single filterable page (replaces tabs + nested regional sub-tabs).
 * Same JSONs, headings and i18n — sections render stacked and react to the
 * cultura/região/período filters. Route url and Ctrl+K index unchanged.
 */
export default function AgricultureAvailabilityPage(): ReactElement {
  const { t: tBody, locale } = useT('agricultural');
  const availData = conabAvailability as AvailabilityRow[];
  const calendarData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;

  const [selectedCrop, setSelectedCrop] = useState<string>(ALL);
  const [selectedRegion, setSelectedRegion] = useState<string>(ALL);
  const [selectedPeriod, setSelectedPeriod] = useState<string>(ALL);

  const stateRegions = useMemo(() => {
    const statesMap: Record<string, StateInfo> = mappingData?.states || {};
    const out: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      out[code] = info.region;
    }
    return out;
  }, [mappingData]);

  const filterOptions = useMemo(() => {
    const crops = new Set<string>();
    const regions = new Set<string>();
    const periods = new Set<string>();
    for (const row of availData) {
      const crop = availCrop(row);
      if (crop !== 'Unknown') crops.add(crop);
      const uf = availUf(row);
      if (uf && stateRegions[uf]) regions.add(stateRegions[uf]);
      for (const p of availPeriods(row)) periods.add(p);
    }
    for (const row of calendarData) {
      const crop = calendarCrop(row);
      if (crop) crops.add(crop);
      const uf = calendarUf(row);
      if (uf && stateRegions[uf]) regions.add(stateRegions[uf]);
    }
    return {
      crops: Array.from(crops).sort(),
      regions: Array.from(regions).sort(),
      periods: Array.from(periods).sort(),
    };
  }, [availData, calendarData, stateRegions]);

  const filteredAvail = useMemo(
    () =>
      availData.filter((row) => {
        if (selectedCrop !== ALL && availCrop(row) !== selectedCrop) return false;
        if (selectedRegion !== ALL && stateRegions[availUf(row)] !== selectedRegion) return false;
        if (selectedPeriod !== ALL && !availPeriods(row).includes(selectedPeriod)) return false;
        return true;
      }),
    [availData, selectedCrop, selectedRegion, selectedPeriod, stateRegions],
  );

  const filteredCalendar = useMemo(
    () =>
      calendarData.filter((row) => {
        if (selectedCrop !== ALL && calendarCrop(row) !== selectedCrop) return false;
        if (selectedRegion !== ALL && stateRegions[calendarUf(row)] !== selectedRegion) return false;
        return true;
      }),
    [calendarData, selectedCrop, selectedRegion, stateRegions],
  );

  // Same parsing as the Plotly original.
  const { stateCoverage, cropDiversity, regionalActivity, activityHeatmap, calendarRecency } = useMemo(() => {
    const cropStates: Record<string, Set<string>> = {};
    const stateYears: Record<string, Set<string>> = {};
    const stateCrops: Record<string, Set<string>> = {};

    for (const row of filteredAvail) {
      const crop = availCrop(row);
      const state = availUf(row);

      if (!state) continue;

      if (!cropStates[crop]) cropStates[crop] = new Set();
      cropStates[crop].add(state);

      if (!stateCrops[state]) stateCrops[state] = new Set();
      stateCrops[state].add(crop);

      for (const period of availPeriods(row)) {
        if (!stateYears[state]) stateYears[state] = new Set();
        stateYears[state].add(period);
      }
    }

    const stateCoverageData = Object.entries(stateCrops)
      .map(([state, crops]) => ({
        name: `${state}${stateRegions[state] ? ` (${translateRegion(stateRegions[state], locale)})` : ''}`,
        value: crops.size,
      }))
      .sort((a, b) => b.value - a.value);

    const cropDiversityData = Object.entries(cropStates)
      .map(([crop, states]) => ({ name: translateCropName(crop, locale), value: states.size }))
      .sort((a, b) => b.value - a.value);

    // Atividade regional em % de UFs ativas (Fase 2): registros tipados
    // agrupados por região, meses em ordem do boletim Out→Set.
    const calendarRecords = toCalendarRecords(
      filteredCalendar.filter((row) => {
        const uf = calendarUf(row);
        return uf !== '' && stateRegions[uf] !== undefined;
      }),
    );
    const byRegion = aggregateSharesByGroup(
      calendarRecords,
      (r) => stateRegions[r.region] ?? r.region,
    );
    const tipLabels: ShareTipLabels = {
      activeUfs: tBody('activeUfsLabel'),
      planting: tBody('tipPlanting'),
      harvest: tBody('tipHarvest'),
      more: (k) => tBody('ufsMore', { k }),
    };
    const currentSlot = bulletinSlotForMonth(currentCalendarMonth());

    const regionLabels = [...byRegion.keys()].sort();
    const translatedMonths = MONTHS_SHORT.map((m, slot) => {
      const label = translateMonthShort(m, locale);
      return slot === currentSlot ? `${label} ●` : label;
    });
    const shareAt = (region: string, slot: number): MonthShare | undefined =>
      byRegion.get(region)?.find((s) => s.month === bulletinIndexToMonth(slot));
    const regionalActivitySeries = regionLabels.map(region => ({
      name: translateRegion(region, locale),
      values: MONTHS_SHORT.map((_, slot) => Math.round(shareAt(region, slot)?.pctActive ?? 0)),
    }));

    const heatmapZ: number[][] = regionLabels.map((r) =>
      MONTHS_SHORT.map((_, slot) => Math.round(shareAt(r, slot)?.pctActive ?? 0)),
    );
    const heatmapTips: (string | null)[][] = regionLabels.map((r) =>
      MONTHS_SHORT.map((_, slot) => {
        const share = shareAt(r, slot);
        if (share === undefined || share.totalUfs === 0) return null;
        return formatShareTip(
          `${translateRegion(r, locale)} · ${translatedMonths[slot]}`,
          share,
          tipLabels,
        );
      }),
    );

    return {
      stateCoverage: {
        labels: stateCoverageData.map(s => s.name),
        values: stateCoverageData.map(s => s.value),
      },
      cropDiversity: {
        labels: cropDiversityData.map(c => c.name),
        values: cropDiversityData.map(c => c.value),
      },
      regionalActivity: {
        categories: translatedMonths,
        series: regionalActivitySeries,
      },
      activityHeatmap: {
        z: heatmapZ,
        tips: heatmapTips,
        regions: regionLabels.map((r) => translateRegion(r, locale)),
        months: translatedMonths,
      },
      calendarRecency: recencyOf(calendarRecords),
    };
  }, [filteredAvail, filteredCalendar, stateRegions, locale, tBody]);

  const totalStates = stateCoverage.labels.length;
  const totalCrops = cropDiversity.labels.length;
  const totalRegions = activityHeatmap.regions.length;
  const hasActiveFilters = selectedCrop !== ALL || selectedRegion !== ALL || selectedPeriod !== ALL;

  const selectClassName =
    'min-h-[44px] w-full cursor-pointer appearance-none rounded-lg border border-border bg-surface py-2.5 pr-10 pl-3 text-sm text-fg shadow-sm transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';

  const selectChevronClassName =
    'pointer-events-none absolute top-1/2 right-3 -translate-y-1/2 text-fg-muted';

  return (
    <div>
      <fieldset className="mb-6 rounded-xl border border-border bg-card p-4">
        <legend className="px-2 text-sm font-semibold text-fg">{tBody('filtersTitle')}</legend>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="availability-filter-crop" className="mb-1.5 block text-sm font-medium text-fg">
              {tBody('filterCrop')}
            </label>
            <div className="relative">
              <select
                id="availability-filter-crop"
                className={selectClassName}
                value={selectedCrop}
                onChange={(event) => setSelectedCrop(event.target.value)}
              >
                <option value={ALL}>{tBody('allCrops')}</option>
                {filterOptions.crops.map((crop) => (
                  <option key={crop} value={crop}>
                    {translateCropName(crop, locale)}
                  </option>
                ))}
              </select>
              <ChevronDown size={16} aria-hidden="true" className={selectChevronClassName} />
            </div>
          </div>
          <div>
            <label htmlFor="availability-filter-region" className="mb-1.5 block text-sm font-medium text-fg">
              {tBody('filterRegion')}
            </label>
            <div className="relative">
              <select
                id="availability-filter-region"
                className={selectClassName}
                value={selectedRegion}
                onChange={(event) => setSelectedRegion(event.target.value)}
              >
                <option value={ALL}>{tBody('allRegions')}</option>
                {filterOptions.regions.map((region) => (
                  <option key={region} value={region}>
                    {translateRegion(region, locale)}
                  </option>
                ))}
              </select>
              <ChevronDown size={16} aria-hidden="true" className={selectChevronClassName} />
            </div>
          </div>
          <div>
            <label htmlFor="availability-filter-period" className="mb-1.5 block text-sm font-medium text-fg">
              {tBody('filterPeriod')}
            </label>
            <div className="relative">
              <select
                id="availability-filter-period"
                className={selectClassName}
                value={selectedPeriod}
                onChange={(event) => setSelectedPeriod(event.target.value)}
              >
                <option value={ALL}>{tBody('allPeriods')}</option>
                {filterOptions.periods.map((period) => (
                  <option key={period} value={period}>
                    {period}
                  </option>
                ))}
              </select>
              <ChevronDown size={16} aria-hidden="true" className={selectChevronClassName} />
            </div>
          </div>
        </div>
        {hasActiveFilters && (
          <button
            type="button"
            className="mt-4 inline-flex min-h-[44px] items-center rounded-lg border border-border px-4 py-2 text-sm font-medium text-fg-secondary transition-colors hover:bg-surface-hover hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            onClick={() => {
              setSelectedCrop(ALL);
              setSelectedRegion(ALL);
              setSelectedPeriod(ALL);
            }}
          >
            {tBody('clearFilters')}
          </button>
        )}
      </fieldset>

      <div className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard icon={Map} label={tBody('metricStatesAvail')} value={totalStates} variant="accuracy" />
          <MetricCard icon={Wheat} label={tBody('metricCropsAvailable')} value={totalCrops} variant="resolution" />
          <MetricCard icon={MapPin} label={tBody('metricRegions')} value={totalRegions} variant="classes" />
        </div>
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hSpatialCoverage')}</h3>
          {stateCoverage.values.length > 0 ? (
            <EChartsHorizontalBar
              labels={stateCoverage.labels}
              values={stateCoverage.values}
              captionKey="cropsAvailable"
              height={Math.max(300, stateCoverage.labels.length * 25)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noSpatialData')}</p>
          )}
        </Card>
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropDiversity')}</h3>
          {cropDiversity.values.length > 0 ? (
            <EChartsHorizontalBar
              labels={cropDiversity.labels}
              values={cropDiversity.values}
              captionKey="statesCount"
              height={Math.max(300, cropDiversity.labels.length * 35)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noDiversityData')}</p>
          )}
        </Card>
        <Card padding="lg" hover={false}>
          <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="text-base font-semibold text-fg">{tBody('hRegionalComparison')}</h3>
            <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
          </div>
          {regionalActivity.series.length > 0 ? (
            <EChartsGroupedBar
              categories={regionalActivity.categories}
              series={regionalActivity.series}
              captionKey="shareActiveUfs"
              height={400}
            />
          ) : (
            <p className="text-fg-muted text-center py-8" role="status">{tBody('noRegionalActivity')}</p>
          )}
        </Card>
        <Card padding="lg" hover={false}>
          <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
            <h3 className="text-base font-semibold text-fg">{tBody('hRegionalHeatmap')}</h3>
            <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
          </div>
          {activityHeatmap.regions.length > 0 ? (
            <>
              <EChartsHeatmap
                z={activityHeatmap.z}
                x={activityHeatmap.months}
                y={activityHeatmap.regions}
                captionKey="activityIntensityByRegionMonth"
                height={Math.max(300, activityHeatmap.regions.length * 60 + 100)}
                min={0}
                max={100}
                showValues
                valueSuffix="%"
                tips={activityHeatmap.tips}
              />
              <div className="mt-3">
                <RecencyBadge recency={calendarRecency} />
              </div>
            </>
          ) : (
            <p className="text-fg-muted text-center py-8" role="status">{tBody('noHeatmapData')}</p>
          )}
        </Card>
      </div>
    </div>
  );
}
