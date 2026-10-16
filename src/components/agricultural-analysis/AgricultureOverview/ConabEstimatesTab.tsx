import { useMemo } from 'react';
import { Package, Sprout, TrendingUp, Wheat } from 'lucide-react';
import Card from '../../ui/Card';
import MetricCard from '../../ui/MetricCard';
import EChartsLine from '../../charts/echarts/EChartsLine';
import EChartsGroupedBar from '../../charts/echarts/EChartsGroupedBar';
import EChartsHorizontalBar from '../../charts/echarts/EChartsHorizontalBar';
import SeasonCloseChart from './SeasonCloseChart';
import { useT } from '../../../i18n/LanguageContext';
import { translateActivity, translateCropName } from '../../../data/glossary';
import { formatKpiArea, formatKpiProduction, formatProductivity } from '../../../lib/format';
import conabAgriculturalData from '../../../data/processed/conab_agricultural_data.json';

interface ProductionYear {
  production: number;
  area: number;
  productivity: number;
}

interface CropData {
  name: string;
  scientific_name?: string;
  production_data?: Record<string, ProductionYear>;
}

interface ConabAgriData {
  metadata?: {
    source?: string;
    description?: string;
    source_url?: string;
    unit_production?: string;
    unit_area?: string;
    total_crops?: number;
  };
  crops?: Record<string, CropData>;
}

export default function ConabEstimatesTab() {
  const { t: tBody, locale } = useT('agricultural');
  const data = conabAgriculturalData as ConabAgriData;
  const crops = data?.crops;

  const metrics = useMemo(() => {
    if (!crops) return { totalProduction: 0, totalArea: 0, avgProductivity: 0, cropCount: 0 };

    let totalProd = 0;
    let totalArea = 0;
    let totalProdWeighted = 0;
    let cropCount = 0;
    const seasons = ['2024/25', '2023/24', '2022/23', '2021/22', '2020/21', '2019/20', '2018/19'];
    const latestSeason = seasons[0];

    for (const [, crop] of Object.entries(crops)) {
      const pd = crop.production_data;
      if (pd && pd[latestSeason]) {
        totalProd += pd[latestSeason].production;
        totalArea += pd[latestSeason].area;
        totalProdWeighted += pd[latestSeason].production * pd[latestSeason].productivity;
        cropCount++;
      }
    }

    const avgProd = totalProd > 0 ? totalProdWeighted / totalProd : 0;

    return {
      totalProduction: totalProd,
      totalArea,
      avgProductivity: Math.round(avgProd),
      cropCount,
    };
  }, [crops]);

  const productionEvolution = useMemo(() => {
    if (!crops) return { series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24', '2024/25', '2025/26'];

    const totalBySeason: Record<string, number> = {};
    for (const season of seasons) {
      totalBySeason[season] = 0;
      for (const [, crop] of Object.entries(crops)) {
        const pd = crop.production_data;
        if (pd && pd[season]) {
          totalBySeason[season] += pd[season].production;
        }
      }
    }

    return {
      series: [{
        name: translateActivity('Total Production (thousand tons)', locale),
        x: seasons,
        y: seasons.map(s => totalBySeason[s]),
      }],
    };
  }, [crops, locale]);

  const cropComparison = useMemo(() => {
    if (!crops) return { categories: [], series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24', '2024/25', '2025/26'];

    const productionSeries = Object.entries(crops).map(([, crop]) => ({
      name: translateCropName(crop.name, locale),
      values: seasons.map((s) => {
        const pd = crop.production_data;
        return pd && pd[s] ? pd[s].production : 0;
      }),
    }));

    return { categories: seasons, series: productionSeries };
  }, [crops, locale]);

  const cropProductivity = useMemo(() => {
    if (!crops) return { series: [] };
    const seasons = ['2018/19', '2019/20', '2020/21', '2021/22', '2022/23', '2023/24', '2024/25', '2025/26'];

    const series: { name: string; x: string[]; y: number[] }[] = [];
    for (const [, crop] of Object.entries(crops)) {
      if (crop.production_data) {
        series.push({
          name: translateCropName(crop.name, locale),
          x: seasons,
          y: seasons.map((s) => crop.production_data?.[s]?.productivity ?? 0),
        });
      }
    }

    return { series };
  }, [crops, locale]);

  const allCropsProduction = useMemo(() => {
    if (!crops) return { labels: [], values: [] };
    const latestSeason = '2024/25'; // last closed harvest (2025/26 is forecast)
    const items: { label: string; value: number }[] = [];

    for (const [, crop] of Object.entries(crops)) {
      const pd = crop.production_data;
      if (pd && pd[latestSeason] && pd[latestSeason].production > 0) {
        items.push({ label: translateCropName(crop.name, locale), value: pd[latestSeason].production });
      }
    }

    items.sort((a, b) => a.value - b.value);
    return {
      labels: items.map(i => i.label),
      values: items.map(i => i.value),
    };
  }, [crops, locale]);

  if (!crops || Object.keys(crops).length === 0) {
    return (
      <div className="p-8 text-center text-fg-secondary">
        <p className="text-lg">{tBody('noConabEstimates')}</p>
        <p className="text-sm mt-2">{tBody('badEstimatesFormat')}</p>
      </div>
    );
  }


  return (
    <div className="space-y-6">
      {/* Metrics Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={Package} label={tBody('metricTotalProduction')} value={formatKpiProduction(metrics.totalProduction, locale)} help={tBody('kpiProductionUnit')} variant="accuracy" />
        <MetricCard icon={Sprout} label={tBody('metricPlantedArea')} value={formatKpiArea(metrics.totalArea, locale)} help={tBody('kpiAreaUnit')} variant="resolution" />
        <MetricCard icon={TrendingUp} label={tBody('metricAvgProductivity')} value={formatProductivity(metrics.avgProductivity, locale)} variant="classes" />
        <MetricCard icon={Wheat} label={tBody('metricCropsTracked')} value={metrics.cropCount} variant="frequency" />
      </div>

      {/* Production Evolution */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hProductionEvolution')}</h3>
        <EChartsLine
          series={productionEvolution.series}
          captionKey="agriProductionEvolution"
          height={350}
        />
      </Card>

      {/* Crop Comparison */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hCropComparison')}</h3>
        <EChartsGroupedBar
          categories={cropComparison.categories}
          series={cropComparison.series}
          captionKey="production"
          height={400}
        />
      </Card>

      {/* Productivity by crop (multi-series line, CONAB kg/ha) */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hConabProductivity')}</h3>
        <EChartsLine
          series={cropProductivity.series}
          captionKey="conabProductivityCaption"
          height={350}
        />
      </Card>

      {/* Season close-out 24/25 × 25/26 (grouped bar + Δ % table) */}
      <SeasonCloseChart />

      {/* All Crops by Production (horizontal bar kept; pie por safra removido P2b) */}
      <Card padding="lg" hover={false}>
        <h3 className="text-base font-semibold text-fg mb-3">{tBody('hAllCrops')}</h3>
        {allCropsProduction.values.length > 0 ? (
          <EChartsHorizontalBar
            labels={allCropsProduction.labels}
            values={allCropsProduction.values}
            captionKey="production"
            height={Math.max(250, allCropsProduction.labels.length * 40)}
          />
        ) : (
          <p className="text-fg-muted text-center py-8">{tBody('noProductionData')}</p>
        )}
      </Card>

      {/* Source Info */}
      <Card padding="md" hover={false}>
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-sm font-semibold text-fg">{tBody('dataSource')}</h4>
            <p className="text-xs text-fg-secondary">
              {data?.metadata?.source || 'CONAB'} &mdash; {data?.metadata?.description || 'Agricultural Production Data'}
            </p>
          </div>
          <a
            href={data?.metadata?.source_url || 'https://www.gov.br/conab/pt-br'}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-amber-700 hover:text-amber-800 underline"
          >
            {tBody('visitSource')}
          </a>
        </div>
      </Card>
    </div>
  );
}
