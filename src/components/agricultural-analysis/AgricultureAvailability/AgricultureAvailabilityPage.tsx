import { useMemo, useState, type ReactElement } from 'react';
import { Map, Wheat, MapPin } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import conabAvailability from '../../../data/processed/conab_availability.json';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateCropName,
  translateMonthShort,
  translateRegion,
} from '../../../data/glossary';

const MONTHS_SHORT = ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep'];

interface AvailabilityRow {
  'Crop Type;Area;Anos (1S);Anos (2S)': string;
  crop?: string;
  uf?: string;
  anos_1s?: string[];
  anos_2s?: string[];
}

interface CalendarRow {
  'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September': string;
  crop?: string;
  uf?: string;
  months?: string[];
}

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
}

const ALL = 'all';

function parseActivityValue(val: string): number {
  if (!val || val.trim() === '') return 0;
  const v = val.trim();
  if (v === 'P' || v === 'H' || v === 'PH') return 1;
  return 0;
}

/** Typed fields first (conab_availability.json), legacy `;`-joined string as fallback. */
function availCrop(row: AvailabilityRow): string {
  if (row.crop && row.crop.trim() !== '') return row.crop.trim();
  const entry = row['Crop Type;Area;Anos (1S);Anos (2S)'];
  const crop = entry?.split(';')[0]?.trim();
  return crop && crop !== '' ? crop : 'Unknown';
}

function availUf(row: AvailabilityRow): string {
  if (row.uf && row.uf.trim() !== '') return row.uf.trim();
  const entry = row['Crop Type;Area;Anos (1S);Anos (2S)'];
  return entry?.split(';')[1]?.trim() ?? '';
}

function availPeriods(row: AvailabilityRow): string[] {
  const out = [...(row.anos_1s ?? []), ...(row.anos_2s ?? [])].map((p) => p.trim()).filter(Boolean);
  if (out.length > 0) return out;
  const entry = row['Crop Type;Area;Anos (1S);Anos (2S)'];
  if (!entry) return [];
  const parts = entry.split(';');
  const periods: string[] = [];
  for (const idx of [2, 3]) {
    const chunk = parts[idx]?.trim();
    if (chunk) {
      for (const p of chunk.split(',')) {
        const period = p.trim();
        if (period) periods.push(period);
      }
    }
  }
  return periods;
}

function calendarUf(row: CalendarRow): string {
  if (row.uf && row.uf.trim() !== '') return row.uf.trim();
  const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
  if (!entry || entry.trim() === '' || entry.startsWith(';')) return '';
  return entry.split(';')[1]?.trim() ?? '';
}

function calendarCrop(row: CalendarRow): string {
  if (row.crop && row.crop.trim() !== '') return row.crop.trim();
  const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
  if (!entry || entry.trim() === '' || entry.startsWith(';')) return '';
  return entry.split(';')[0]?.trim() ?? '';
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
  const { stateCoverage, cropDiversity, regionalActivity, activityHeatmap } = useMemo(() => {
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

    const regionMonthActivity: Record<string, number[]> = {};

    for (const row of filteredCalendar) {
      const uf = calendarUf(row);
      const region = stateRegions[uf];
      if (!uf || !region) continue;

      const typedMonths = row.months;
      if (typedMonths && typedMonths.length >= 12) {
        if (!regionMonthActivity[region]) {
          regionMonthActivity[region] = MONTHS_SHORT.map(() => 0);
        }
        typedMonths.slice(0, 12).forEach((v, i) => {
          if (parseActivityValue(v) > 0) {
            regionMonthActivity[region][i]++;
          }
        });
        continue;
      }

      const entry = row['Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September'];
      if (!entry || entry.trim() === '' || entry.startsWith(';')) continue;

      const parts = entry.split(';');
      if (parts.length < 13) continue;

      if (!regionMonthActivity[region]) {
        regionMonthActivity[region] = MONTHS_SHORT.map(() => 0);
      }

      parts.slice(2).forEach((v, i) => {
        if (parseActivityValue(v) > 0) {
          regionMonthActivity[region][i]++;
        }
      });
    }

    const regionLabels = Object.keys(regionMonthActivity).sort();
    const translatedMonths = MONTHS_SHORT.map((m) => translateMonthShort(m, locale));
    const regionalActivitySeries = regionLabels.map(region => ({
      name: translateRegion(region, locale),
      values: regionMonthActivity[region],
    }));

    const heatmapZ: number[][] = regionLabels.map(r => regionMonthActivity[r]);

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
        regions: regionLabels.map((r) => translateRegion(r, locale)),
        months: translatedMonths,
      },
    };
  }, [filteredAvail, filteredCalendar, stateRegions, locale]);

  const totalStates = stateCoverage.labels.length;
  const totalCrops = cropDiversity.labels.length;
  const totalRegions = activityHeatmap.regions.length;
  const hasActiveFilters = selectedCrop !== ALL || selectedRegion !== ALL || selectedPeriod !== ALL;

  const selectClassName =
    'mt-1 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary';

  return (
    <div>
      <fieldset className="mb-6 rounded-xl border border-border bg-card p-4">
        <legend className="px-2 text-sm font-semibold text-fg">{tBody('filtersTitle')}</legend>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <label htmlFor="availability-filter-crop" className="text-sm font-medium text-fg">
              {tBody('filterCrop')}
            </label>
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
          </div>
          <div>
            <label htmlFor="availability-filter-region" className="text-sm font-medium text-fg">
              {tBody('filterRegion')}
            </label>
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
          </div>
          <div>
            <label htmlFor="availability-filter-period" className="text-sm font-medium text-fg">
              {tBody('filterPeriod')}
            </label>
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
          </div>
        </div>
        {hasActiveFilters && (
          <button
            type="button"
            className="mt-4 rounded-lg border border-border px-3 py-1.5 text-sm font-medium text-fg-secondary transition-colors hover:bg-surface-hover hover:text-fg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
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
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hRegionalComparison')}</h3>
          {regionalActivity.series.length > 0 ? (
            <EChartsGroupedBar
              categories={regionalActivity.categories}
              series={regionalActivity.series}
              captionKey="activityCount"
              height={400}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noRegionalActivity')}</p>
          )}
        </Card>
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hRegionalHeatmap')}</h3>
          {activityHeatmap.regions.length > 0 ? (
            <EChartsHeatmap
              z={activityHeatmap.z}
              x={activityHeatmap.months}
              y={activityHeatmap.regions}
              captionKey="activityIntensityByRegionMonth"
              height={Math.max(300, activityHeatmap.regions.length * 60 + 100)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noHeatmapData')}</p>
          )}
        </Card>
      </div>
    </div>
  );
}
