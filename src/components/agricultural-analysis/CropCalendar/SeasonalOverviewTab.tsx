import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import { LANDAGRI_COLORWAY_DARK, LANDAGRI_COLORWAY_LIGHT } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import { translateActivity, translateSeason } from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';
import { activityFromCode, type ConabCalendarRow } from '../../../types/calendar';

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

  const seasonalData = useMemo(() => {
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

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

    for (const row of rawData) {
      const crop = (row.crop || '').trim();
      if (crop === '' || !selectedCrops.includes(crop)) continue;

      const state = (row.uf || '').trim();
      if (state === '') continue;
      const region = stateRegions[state];
      if (region !== undefined && !selectedRegions.includes(region)) continue;
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
    const way = theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;

    return {
      categories: seasonNames.map((s) => translateSeason(s, locale)),
      series: [
        { name: translateActivity('Planting', locale), values: seasonNames.map((s) => pct(plantUfs[s])), color: way[0] },
        { name: translateActivity('Harvest', locale), values: seasonNames.map((s) => pct(harvestUfs[s])), color: way[5] },
      ],
      empty: scopeUfs.size === 0,
    };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale, theme]);

  return (
    <Card padding="lg" hover={false}>
      <div className="mb-2 flex flex-wrap items-baseline justify-between gap-2">
        <h3 className="text-base font-semibold text-fg">{tBody('hSeasonal')}</h3>
        <span className="text-xs font-medium text-fg-secondary">{tBody('shareModeUf')}</span>
      </div>
      {seasonalData.empty ? (
        <p className="text-fg-muted text-center py-8" role="status">{tBody('noFilterData')}</p>
      ) : (
        <EChartsGroupedBar
          categories={seasonalData.categories}
          series={seasonalData.series}
          captionKey="shareSplitMonthly"
          height={400}
        />
      )}
      <div className="mt-4 p-3 bg-surface-alt rounded-lg">
        <p className="text-xs text-fg-secondary">
          <strong>{tBody('noteLabel')}</strong> {tBody('seasonNote')}
        </p>
      </div>
    </Card>
  );
}
