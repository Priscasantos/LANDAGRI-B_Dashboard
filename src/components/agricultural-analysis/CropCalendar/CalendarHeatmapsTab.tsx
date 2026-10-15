import { useMemo } from 'react';
import Card from '../../ui/Card';
import EChartsHeatmap from '../../charts/echarts/EChartsHeatmap';
import { HEATMAP_EMPTY_CELL_DARK, HEATMAP_EMPTY_CELL_LIGHT, LANDAGRI_COLORWAY_DARK, LANDAGRI_COLORWAY_LIGHT } from '../../../lib/echarts-theme';
import { useEffectiveTheme } from '../../../hooks/use-theme';
import { useT } from '../../../i18n/LanguageContext';
import { translateCropName, translateMonth } from '../../../data/glossary';
import conabCalendar from '../../../data/processed/conab_calendar.json';
import conabMapping from '../../../data/processed/conab_mapping.json';

const MONTHS = ['October', 'November', 'December', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September'];

interface CalendarRow {
  'Crop type;Federation Unit;October;November;December;January;February;March;April;May;June;July;August;September': string;
}

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

function parseActivityValue(val: string): number {
  if (!val || val.trim() === '') return 0;
  const v = val.trim();
  if (v === 'PH') return 3; // both planting and harvest
  if (v === 'P') return 1; // planting
  if (v === 'H') return 2; // harvest
  return 0;
}

export default function CalendarHeatmapsTab({ selectedCrops, selectedRegions }: CalendarHeatmapsTabProps) {
  const { t } = useT('charts');
  const { t: tBody, locale } = useT('agricultural');
  const theme = useEffectiveTheme();
  const rawData = conabCalendar as CalendarRow[];
  const mappingData = conabMapping as MappingDataType;
  const statesMap = mappingData?.states || {};

  const matrix = useMemo(() => {
    const crops = [...new Set(selectedCrops)];
    const monthIndices = MONTHS.map((_, i) => i);

    // Build state-region lookup
    const stateRegions: Record<string, string> = {};
    for (const [code, info] of Object.entries(statesMap)) {
      stateRegions[code] = info.region;
    }

    // Filter the raw CSV-like data
    const filtered: { crop: string; state: string; activities: number[] }[] = [];

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
      filtered.push({ crop, state, activities });
    }

    // National matrix: crops x months showing sum of activities
    const nationalZ: number[][] = [];
    const cropLabels: string[] = [];

    for (const crop of crops) {
      const cropEntries = filtered.filter(f => f.crop === crop);
      if (cropEntries.length === 0) continue;
      cropLabels.push(translateCropName(crop, locale));

      const monthSums = monthIndices.map(m => {
        let sum = 0;
        let hasPlanting = false;
        let hasHarvest = false;
        for (const entry of cropEntries) {
          const val = entry.activities[m];
          if (val === 1 || val === 3) hasPlanting = true;
          if (val === 2 || val === 3) hasHarvest = true;
        }
        if (hasPlanting && hasHarvest) sum = 3;
        else if (hasPlanting) sum = 1;
        else if (hasHarvest) sum = 2;
        return sum;
      });
      nationalZ.push(monthSums);
    }

    return { z: nationalZ, crops: cropLabels, months: MONTHS.map((m) => translateMonth(m, locale)) };
  }, [rawData, selectedCrops, selectedRegions, statesMap, locale]);

  // Cores por categoria a partir do colorway do tema ativo (0=ausente neutro,
  // 1=plantio verde, 2=colheita terra, 3=ambos teal) — semântica preservada
  // nos dois temas em vez do hex fixo herdado.
  const way = theme === 'dark' ? LANDAGRI_COLORWAY_DARK : LANDAGRI_COLORWAY_LIGHT;
  const colorscale = [
    theme === 'dark' ? HEATMAP_EMPTY_CELL_DARK : HEATMAP_EMPTY_CELL_LIGHT,
    way[0],
    way[5],
    way[7],
  ];

  if (matrix.crops.length === 0) {
    return (
      <Card padding="lg" hover={false}>
        <div className="p-8 text-center text-fg-secondary">
          <p>{tBody('noCalendarData')}</p>
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-2">{tBody('hNationalMatrix')}</h3>
        <p className="text-xs text-fg-secondary mb-4">
          {tBody('matrixLegend')}
        </p>
        <EChartsHeatmap
          z={matrix.z}
          x={matrix.months}
          y={matrix.crops}
          captionKey="cropCalendarActivity"
          height={Math.max(300, matrix.crops.length * 50 + 100)}
          colors={colorscale}
          min={0}
          max={3}
        />
      </Card>

      {/* Legend */}
      <Card padding="md" hover={false}>
        <div className="flex items-center gap-6 flex-wrap">
          <span className="text-sm font-medium text-fg-secondary">{t('legend')}:</span>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded bg-green-500 inline-block" />
            <span className="text-xs text-fg-secondary">{t('planting')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded bg-orange-500 inline-block" />
            <span className="text-xs text-fg-secondary">{t('harvest')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded bg-blue-500 inline-block" />
            <span className="text-xs text-fg-secondary">{t('plantingHarvest')}</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-4 rounded bg-surface-alt inline-block" />
            <span className="text-xs text-fg-secondary">{t('noActivity')}</span>
          </div>
        </div>
      </Card>
    </div>
  );
}
