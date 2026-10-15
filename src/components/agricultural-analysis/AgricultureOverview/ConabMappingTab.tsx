import { useMemo } from 'react';
import { Wheat, Map, MapPin, CalendarDays, Download } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsLine from '../../charts/echarts/EChartsLine';
import { useT } from '../../../i18n/LanguageContext';
import { formatCropName } from '../../../lib/cropNames';
import conabMapping from '../../../data/processed/conab_mapping.json';
import conabMappingData from '../../../data/processed/conab_mapping_data.json';

interface StateInfo {
  name: string;
  region: string;
}

interface CropMappingEntry {
  name: string;
  scientific_name?: string;
  mapping_years?: string[];
  total_area_mapped_2024?: number;
  main_regions?: string[];
  accuracy?: number;
  data_sources?: string[];
  mapping_method?: string;
}

interface ConabMappingDataType {
  metadata?: {
    source?: string;
    description?: string;
    temporal_coverage?: string;
    spatial_resolution?: string;
  };
  crops_mapping?: Record<string, CropMappingEntry>;
}

// Types for JSON imports
interface CalendarEntry {
  state_code: string;
  state_name: string;
  region: string;
  calendar: Record<string, string>;
}

interface MappingDataType {
  metadata?: {
    source?: string;
    description?: string;
    seasons?: Record<string, { period: string; months: string[] }>;
    legend?: Record<string, string>;
  };
  states?: Record<string, StateInfo>;
  crop_calendar?: Record<string, CalendarEntry[]>;
}

type MappingData = MappingDataType;
export default function ConabMappingTab() {
  const { t } = useT('charts');
  const { t: tBody } = useT('agricultural');
  const mappingData = conabMapping as MappingData;
  const mappingDataDetailed = conabMappingData as ConabMappingDataType;

  const metrics = useMemo(() => {
    const calendar = mappingData?.crop_calendar;
    const cropCount = calendar ? Object.keys(calendar).length : 0;
    const states = mappingData?.states;
    const stateCount = states ? Object.keys(states).length : 0;
    const regions = states
      ? [...new Set(Object.values(states).map((s: StateInfo) => s.region))].length
      : 0;
    return { cropCount, stateCount, regionCount: regions };
  }, [mappingData]);

  const cropRegionData = useMemo(() => {
    const calendar = mappingData?.crop_calendar;
    if (!calendar) return { categories: [], series: [] };

    const regions = ['North', 'Northeast', 'Central-West', 'Southeast', 'South'];
    const crops = Object.keys(calendar);
    const regionCounts: Record<string, Record<string, number>> = {};

    for (const crop of crops) {
      regionCounts[crop] = {};
      for (const region of regions) {
        regionCounts[crop][region] = 0;
      }
      for (const entry of calendar[crop]) {
        if (regionCounts[crop][entry.region] !== undefined) {
          regionCounts[crop][entry.region]++;
        }
      }
    }

    return {
      categories: regions,
      series: crops.map(crop => ({
        name: formatCropName(crop),
        values: regions.map(r => regionCounts[crop][r] || 0),
      })),
    };
  }, [mappingData]);

  const temporalData = useMemo(() => {
    const cropsMapping = mappingDataDetailed?.crops_mapping;
    if (!cropsMapping) return { series: [] };

    const years = ['2020', '2021', '2022', '2023', '2024'];
    // Numeric years (not date-like strings) so Plotly uses a linear axis;
    // combined with `dtick: 1` + `tickformat: 'd'` below, ticks are always
    // whole years — never fractional labels like "2020.5".
    const numericYears = years.map(Number);
    const series = Object.entries(cropsMapping).map(([, crop]) => ({
      name: crop.name,
      x: numericYears,
      y: years.map(y => (crop.mapping_years?.includes(y) ? 1 : 0)),
    }));

    return { series };
  }, [mappingDataDetailed]);

  if (!mappingData?.crop_calendar) {
    return (
      <div className="p-8 text-center text-fg-secondary">
        <p className="text-lg">{tBody('noConabMapping')}</p>
        <p className="text-sm mt-2">{tBody('badMappingFormat')}</p>
      </div>
    );
  }

  const mappingYears = mappingDataDetailed?.metadata?.temporal_coverage || '2020-2024';
  const sourceUrl = 'https://portaldeinformacoes.conab.gov.br/mapeamentos-agricolas-downloads.html';

  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Wheat} label={tBody('metricTotalCrops')} value={metrics.cropCount} variant="accuracy" />
        <MetricCard icon={Map} label={tBody('metricStatesCovered')} value={metrics.stateCount} variant="resolution" />
        <MetricCard icon={MapPin} label={tBody('metricRegions')} value={metrics.regionCount} variant="classes" />
        <MetricCard icon={CalendarDays} label={tBody('metricTemporalSpan')} value={mappingYears} variant="frequency" />
      </div>

      {/* Crop Regional Distribution */}
      <Card title={t('cropRegionalDistribution')} padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropRegionalDist')}</h3>
        {cropRegionData.series.length > 0 ? (
          <EChartsGroupedBar
            categories={cropRegionData.categories}
            series={cropRegionData.series}
            captionKey="cropRegionalDistribution"
            height={400}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noRegionalData')}</p>
        )}
      </Card>

      {/* Temporal Coverage Evolution */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hTemporalEvolution')}</h3>
        {temporalData.series.length > 0 ? (
          <EChartsLine
            series={temporalData.series}
            captionKey="activeMapping"
            height={350}
            showMarkers={false}
            areaFill
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noTemporalData')}</p>
        )}
      </Card>

      {/* Source Info */}
      <Card padding="md" hover={false}>
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h4 className="text-sm font-semibold text-fg">{tBody('dataSource')}</h4>
            <p className="text-xs text-fg-secondary">
              {mappingData?.metadata?.source || 'CONAB'} &mdash;{' '}
              {mappingData?.metadata?.description || 'Agricultural Mapping Data'}
            </p>
            <p className="text-xs text-fg-muted mt-1">
              {tBody('spatialResolutionLabel')}: {mappingDataDetailed?.metadata?.spatial_resolution || '30m'} |
              {tBody('temporalCoverageLabel')}: {mappingYears}
            </p>
          </div>
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium text-amber-700 bg-amber-50 rounded-lg hover:bg-amber-100 transition-colors"
          >
            <Download size={15} aria-hidden="true" className="shrink-0" />
            {tBody('downloadData')}
          </a>
        </div>
      </Card>
    </div>
  );
}
