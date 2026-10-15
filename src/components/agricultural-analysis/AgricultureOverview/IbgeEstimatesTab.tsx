import { useMemo } from 'react';
import { Wheat, BarChart3, MapPin, TrendingUp, CalendarDays, ClipboardList, RefreshCw } from 'lucide-react';
import Card from '../../ui/Card';
import Tabs from '../../ui/Tabs';
import DataTable from '../../ui/DataTable';
import MetricCard from '../../ui/MetricCard';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import EChartsLine from '../../charts/echarts/EChartsLine';
import { useT } from '../../../i18n/LanguageContext';
import {
  translateActivity,
  translateCropName,
  translateRegion,
  translateTerm,
} from '../../../data/glossary';
import ibgeData from '../../../data/processed/brazilian_ibge_agricultural_data.json';

interface IBGECropEntry {
  name: string;
  code: string;
  production_quantity_tonnes?: Record<string, number>;
  harvested_area_hectares?: Record<string, number>;
  planted_area_hectares?: Record<string, number>;
  average_yield?: Record<string, number>;
  production_value_thousand_reais?: Record<string, number>;
}

interface IBGEDataType {
  metadata?: {
    source?: string;
    survey?: string;
    period_range?: string;
    periodicity?: string;
  };
  data?: {
    agricultural_production?: Record<string, IBGECropEntry>;
  };
}

const REGIONS = ['North', 'Northeast', 'Southeast', 'South', 'Central-West'];

export default function IbgeEstimatesTab() {
  // locale reativo p/ chrome dos gráficos; rótulos de coluna usam o mesmo
  // namespace `charts` (são legendas da tabela de culturas).
  const { t, locale } = useT('charts');
  const { t: tBody, locale: bodyLocale } = useT('agricultural');
  const data = ibgeData as IBGEDataType;
  const production = data?.data?.agricultural_production;

  const years = useMemo(() => {
    if (!production) return [];
    const yearSet = new Set<string>();
    for (const [, crop] of Object.entries(production)) {
      if (crop.production_quantity_tonnes) {
        Object.keys(crop.production_quantity_tonnes).forEach(y => yearSet.add(y));
      }
    }
    return Array.from(yearSet).sort();
  }, [production]);

  const topCrops = useMemo(() => {
    if (!production || years.length === 0) return [];
    const latestYear = years[years.length - 1];
    const items: { name: string; production: number; area: number }[] = [];

    for (const [, crop] of Object.entries(production)) {
      const prod = crop.production_quantity_tonnes?.[latestYear];
      const area = crop.harvested_area_hectares?.[latestYear];
      if (prod && prod > 0) {
        items.push({
          name: translateCropName(crop.name, bodyLocale),
          production: prod,
          area: area || 0,
        });
      }
    }

    items.sort((a, b) => b.production - a.production);
    return items.slice(0, 10);
  }, [production, years, bodyLocale]);

  const totalProductionEvolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const totals: Record<string, number> = {};
    for (const year of years) totals[year] = 0;

    for (const [, crop] of Object.entries(production)) {
      if (crop.production_quantity_tonnes) {
        for (const [year, val] of Object.entries(crop.production_quantity_tonnes)) {
          totals[year] = (totals[year] || 0) + val;
        }
      }
    }

    return {
      series: [{
        name: translateActivity('Total Production (tonnes)', bodyLocale),
        x: years,
        y: years.map(y => totals[y] || 0),
      }],
    };
  }, [production, years, bodyLocale]);

  const areaEvolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const totals: Record<string, number> = {};
    for (const year of years) totals[year] = 0;

    for (const [, crop] of Object.entries(production)) {
      if (crop.harvested_area_hectares) {
        for (const [year, val] of Object.entries(crop.harvested_area_hectares)) {
          totals[year] = (totals[year] || 0) + val;
        }
      }
    }

    return {
      series: [{
        name: translateActivity('Harvested Area (hectares)', bodyLocale),
        x: years,
        y: years.map(y => totals[y] || 0),
      }],
    };
  }, [production, years, bodyLocale]);

  const top5Evolution = useMemo(() => {
    if (!production || years.length === 0) return { series: [] };
    const items: { name: string; production: number }[] = [];
    const latestYear = years[years.length - 1];

    for (const [, crop] of Object.entries(production)) {
      const prod = crop.production_quantity_tonnes?.[latestYear];
      if (prod) items.push({ name: crop.name, production: prod });
    }

    items.sort((a, b) => b.production - a.production);
    const top5 = items.slice(0, 5).map(i => i.name);

    const series = top5.map(name => {
      const entry = Object.values(production).find(c => c.name === name);
      if (!entry?.production_quantity_tonnes) return null;
      return {
        name: translateCropName(name, bodyLocale),
        x: years,
        y: years.map(y => entry.production_quantity_tonnes![y] || 0),
      };
    }).filter(Boolean) as { name: string; x: string[]; y: number[] }[];

    return { series };
  }, [production, years, bodyLocale]);

  const tableColumns = [
    { key: 'name', label: t('crop') },
    { key: 'production', label: `${t('production')} (${t('tonnes')})`, format: (v: unknown) => (v as number)?.toLocaleString(locale) || '-' },
    { key: 'area', label: `${t('harvestedArea')} (ha)`, format: (v: unknown) => (v as number)?.toLocaleString(locale) || '-' },
  ];

  if (!production || Object.keys(production).length === 0) {
    return (
      <div className="p-8 text-center text-fg-secondary">
        <p className="text-lg">{tBody('noIbgeEstimates')}</p>
        <p className="text-sm mt-2">{tBody('badIbgeFormat')}</p>
      </div>
    );
  }

  const productionByCropContent = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hTop10')}</h3>
          {topCrops.length > 0 ? (
            <EChartsHorizontalBar
              labels={topCrops.map(c => c.name)}
              values={topCrops.map(c => c.production / 1000000)}
              captionKey="production"
              height={Math.max(300, topCrops.length * 35)}
            />
          ) : (
            <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
          )}
        </Card>

        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropTable')}</h3>
          <DataTable
            columns={tableColumns}
            data={topCrops as unknown as Record<string, unknown>[]}
          />
        </Card>
      </div>
    </div>
  );

  const regionalContent = (
    <div className="space-y-6">
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hRegionalIndicators')}</h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          {REGIONS.map(region => (
            <div key={region} className="bg-amber-50 rounded-lg p-3 text-center border border-amber-200">
              <p className="text-xs text-amber-700 font-medium">{translateRegion(region, bodyLocale)}</p>
              <p className="text-lg font-bold text-amber-900 mt-1"><Wheat size={20} aria-hidden="true" className="mx-auto" /></p>
              <p className="text-xs text-amber-600">{tBody('majorProducer')}</p>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );

  const historicalContent = (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hTotalProdEvolution')}</h3>
          <EChartsLine
            series={totalProductionEvolution.series}
            captionKey="production"
            height={350}
          />
        </Card>

        <Card padding="lg" hover={false}>
          <h3 className="text-base font-semibold text-fg mb-3">{tBody('hHarvestedArea')}</h3>
          <EChartsLine
            series={areaEvolution.series}
            captionKey="harvestedArea"
            height={350}
          />
        </Card>
      </div>

      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hTop5')}</h3>
        {top5Evolution.series.length > 0 ? (
          <EChartsLine
            series={top5Evolution.series}
            captionKey="production"
            height={400}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noData')}</p>
        )}
      </Card>
    </div>
  );

  const subTabs = [
    { id: 'production', label: tBody('tabProductionByCrop'), icon: BarChart3, content: productionByCropContent },
    { id: 'regional', label: tBody('tabRegionalDist'), icon: MapPin, content: regionalContent },
    { id: 'historical', label: tBody('tabHistorical'), icon: TrendingUp, content: historicalContent },
  ];

  return (
    <div className="space-y-6">
      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={BarChart3} label={tBody('metricCropsTracked')} value={Object.keys(production).length} variant="accuracy" />
        <MetricCard icon={CalendarDays} label={tBody('metricPeriod')} value={data?.metadata?.period_range || years.join('-')} variant="frequency" />
        <MetricCard icon={ClipboardList} label={tBody('metricSurvey')} value={data?.metadata?.survey?.split(' ')[0] || 'PAM'} variant="resolution" />
        <MetricCard icon={RefreshCw} label={tBody('metricFrequency')} value={translateTerm('frequency', data?.metadata?.periodicity || 'Annual', bodyLocale)} variant="classes" />
      </div>

      <Tabs tabs={subTabs} />
    </div>
  );
}
