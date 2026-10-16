import { useMemo } from 'react';
import { LayoutGrid, Sprout, Map as MapIcon } from 'lucide-react';
import Card from '../../ui/Card';
import Tabs from '../../ui/Tabs';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { phenoPhaseColor } from '../../../lib/phenoColors';
import PhenologyLegend from './PhenologyLegend';
import { useT } from '../../../i18n/LanguageContext';
import { translateActivity, translateCropName, translateRegion, translateSeason } from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { activityFromCode, type ConabCalendarRow } from '../../../types/calendar';
import {
  formatBreakdownTip,
  summarizeActivityByGroup,
  toCalendarRecords,
  type ShareTipLabels,
} from '../../../lib/calendarShare';

type CalendarRow = ConabCalendarRow;

interface StateInfo {
  name: string;
  region: string;
}

interface MappingDataType {
  states?: Record<string, StateInfo>;
}

interface SeasonalOverviewTabProps {
  selectedCrops: string[];
  selectedRegions: string[];
}

export default function SeasonalOverviewTab({ selectedCrops, selectedRegions }: SeasonalOverviewTabProps) {
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

    const inScope = (row: CalendarRow): boolean => {
      const crop = (row.crop || '').trim();
      if (crop === '' || !selectedCrops.includes(crop)) return false;
      const state = (row.uf || '').trim();
      if (state === '') return false;
      const region = stateRegions[state];
      if (region !== undefined && !selectedRegions.includes(region)) return false;
      return true;
    };
    const filtered = rawData.filter(inScope);

    // Grupos de slots do boletim (Out→Set) por estação austral.
    const seasons: Record<string, number[]> = {
      'Spring (Oct-Dec)': [0, 1, 2],
      'Summer (Jan-Mar)': [3, 4, 5],
      'Autumn (Apr-Jun)': [6, 7, 8],
      'Winter (Jul-Sep)': [9, 10, 11],
    };

    const seasonNames = Object.keys(seasons);
    const plantUfs: Record<string, Set<string>> = {};
    const harvestUfs: Record<string, Set<string>> = {};
    const scopeUfs = new Set<string>();
    for (const name of seasonNames) {
      plantUfs[name] = new Set();
      harvestUfs[name] = new Set();
    }

    for (const row of filtered) {
      const state = (row.uf || '').trim();
      scopeUfs.add(state);

      // Soma tipada via schema Fase 1 (sem comparar `P`/`H` aqui).
      row.months.slice(0, 12).forEach((code, slot) => {
        const { plantingPct, harvestPct } = activityFromCode(code);
        for (const [seasonName, slots] of Object.entries(seasons)) {
          if (!slots.includes(slot)) continue;
          if (plantingPct > 0) plantUfs[seasonName].add(state);
          if (harvestPct > 0) harvestUfs[seasonName].add(state);
        }
      });
    }

    const denom = Math.max(scopeUfs.size, 1);
    const pct = (set: Set<string>): number => Math.round((set.size / denom) * 100);
    const plantingColor = phenoPhaseColor('P', theme);
    const harvestColor = phenoPhaseColor('H', theme);

    // Breakdowns por cultura e por região: % de células UF×mês com P/H
    // (agregação em código sobre months[] tipado; UF→região via mapping).
    const records = toCalendarRecords(filtered);
    const byCrop = summarizeActivityByGroup(records, (r) => r.cropId);
    const byRegion = summarizeActivityByGroup(records, (r) => stateRegions[r.region] ?? r.region);

    return {
      seasonal: {
        categories: seasonNames.map((s) => translateSeason(s, locale)),
        series: [
          { name: translateActivity('Planting', locale), values: seasonNames.map((s) => pct(plantUfs[s])), color: plantingColor },
          { name: translateActivity('Harvest', locale), values: seasonNames.map((s) => pct(harvestUfs[s])), color: harvestColor },
        ],
        empty: scopeUfs.size === 0,
      },
      byCrop,
      byRegion,
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale, theme]);

  const tipLabels: ShareTipLabels = {
    activeUfs: tBody('activeUfsLabel'),
    planting: tBody('tipPlanting'),
    harvest: tBody('tipHarvest'),
    more: (k) => tBody('ufsMore', { k }),
  };
  const plantingColor = phenoPhaseColor('P', theme);
  const harvestColor = phenoPhaseColor('H', theme);

  // Visão por cultura: barras P/H por cultura com tooltips de UFs.
  const byCropMap = new Map(model.byCrop.map((b) => [b.key, b]));
  const cropKeys = selectedCrops.filter((crop) => byCropMap.has(crop));
  const cropsWithoutActivity = [
    ...selectedCrops.filter((crop) => !byCropMap.has(crop)).map((crop) => translateCropName(crop, locale)),
    ...model.byCrop
      .filter((b) => selectedCrops.includes(b.key) && b.pctPlanting === 0 && b.pctHarvest === 0)
      .map((b) => translateCropName(b.key, locale)),
  ];
  const cropSeries = [
    {
      name: translateActivity('Planting', locale),
      values: cropKeys.map((key) => Math.round(byCropMap.get(key)?.pctPlanting ?? 0)),
      color: plantingColor,
    },
    {
      name: translateActivity('Harvest', locale),
      values: cropKeys.map((key) => Math.round(byCropMap.get(key)?.pctHarvest ?? 0)),
      color: harvestColor,
    },
  ];
  const cropTips: (string | null)[][] = (['planting', 'harvest'] as const).map((slice) =>
    cropKeys.map((key) => {
      const breakdown = byCropMap.get(key);
      if (breakdown === undefined) return null;
      return formatBreakdownTip(translateCropName(key, locale), breakdown, tipLabels, undefined, slice);
    }),
  );

  // Visão por região: mesmo breakdown com UF→região agregada em código.
  const byRegionMap = new Map(model.byRegion.map((b) => [b.key, b]));
  const regionKeys = selectedRegions.filter((region) => byRegionMap.has(region));
  const regionsWithoutActivity = [
    ...selectedRegions.filter((region) => !byRegionMap.has(region)).map((region) => translateRegion(region, locale)),
    ...model.byRegion
      .filter((b) => selectedRegions.includes(b.key) && b.pctPlanting === 0 && b.pctHarvest === 0)
      .map((b) => translateRegion(b.key, locale)),
  ];
  const regionSeries = [
    {
      name: translateActivity('Planting', locale),
      values: regionKeys.map((key) => Math.round(byRegionMap.get(key)?.pctPlanting ?? 0)),
      color: plantingColor,
    },
    {
      name: translateActivity('Harvest', locale),
      values: regionKeys.map((key) => Math.round(byRegionMap.get(key)?.pctHarvest ?? 0)),
      color: harvestColor,
    },
  ];
  const regionTips: (string | null)[][] = (['planting', 'harvest'] as const).map((slice) =>
    regionKeys.map((key) => {
      const breakdown = byRegionMap.get(key);
      if (breakdown === undefined) return null;
      return formatBreakdownTip(translateRegion(key, locale), breakdown, tipLabels, undefined, slice);
    }),
  );

  const overviewContent = (
    <Card padding="lg" hover={false}>
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hSeasonal')}</h3>
        <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
      </div>
      {model.seasonal.empty ? (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      ) : (
        <EChartsGroupedBar
          categories={model.seasonal.categories}
          series={model.seasonal.series}
          captionKey="shareSplitMonthly"
          height={400}
        />
      )}
      <div className="mt-4">
        <PhenologyLegend />
      </div>
      <div className="mt-4 p-3 bg-surface-alt rounded-lg">
        <p className="text-xs text-fg-secondary">
          <strong>{tBody('noteLabel')}</strong> {tBody('seasonNote')}
        </p>
      </div>
    </Card>
  );

  const cropContent = (
    <Card padding="lg" hover={false}>
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hSeasonalByCrop')}</h3>
        <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
      </div>
      {cropKeys.length === 0 ? (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      ) : (
        <EChartsGroupedBar
          categories={cropKeys.map((crop) => translateCropName(crop, locale))}
          series={cropSeries}
          tips={cropTips}
          captionKey="shareSplitMonthly"
          height={400}
        />
      )}
      {cropKeys.length > 0 && cropsWithoutActivity.length > 0 ? (
        <p className="text-fg-muted text-center text-sm py-4" role="status">
          {tBody('emptyGroupNoData', { names: cropsWithoutActivity.join(', ') })}
        </p>
      ) : null}
      <div className="mt-4">
        <PhenologyLegend />
      </div>
      <div className="mt-4 p-3 bg-surface-alt rounded-lg">
        <p className="text-xs text-fg-secondary">
          <strong>{tBody('noteLabel')}</strong> {tBody('breakdownNote')}
        </p>
      </div>
    </Card>
  );

  const regionContent = (
    <Card padding="lg" hover={false}>
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hSeasonalByRegion')}</h3>
        <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
      </div>
      {regionKeys.length === 0 ? (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      ) : (
        <EChartsGroupedBar
          categories={regionKeys.map((region) => translateRegion(region, locale))}
          series={regionSeries}
          tips={regionTips}
          captionKey="shareSplitMonthly"
          height={400}
        />
      )}
      {regionKeys.length > 0 && regionsWithoutActivity.length > 0 ? (
        <p className="text-fg-muted text-center text-sm py-4" role="status">
          {tBody('emptyGroupNoData', { names: regionsWithoutActivity.join(', ') })}
        </p>
      ) : null}
      <div className="mt-4">
        <PhenologyLegend />
      </div>
      <div className="mt-4 p-3 bg-surface-alt rounded-lg">
        <p className="text-xs text-fg-secondary">
          <strong>{tBody('noteLabel')}</strong> {tBody('breakdownNote')}
        </p>
      </div>
    </Card>
  );

  const subTabs = [
    { id: 'overview', label: tBody('viewOverview'), icon: LayoutGrid, content: overviewContent },
    { id: 'by-crop', label: tBody('viewByCrop'), icon: Sprout, content: cropContent },
    { id: 'by-region', label: tBody('viewByRegion'), icon: MapIcon, content: regionContent },
  ];

  return <Tabs tabs={subTabs} label={tBody('tabSeasonal')} />;
}
